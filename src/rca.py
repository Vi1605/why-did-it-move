import pandas as pd

DIMENSIONS = ["channel", "region", "age_band", "product"]


def contribution_analysis(df, dim, base_month, cur_month, metric="renewed"):
    """Split the change in the overall rate into per-segment rate and mix effects."""
    base = df[df["renewal_month"] == pd.Timestamp(base_month)]
    cur = df[df["renewal_month"] == pd.Timestamp(cur_month)]

    def summarise(d):
        g = d.groupby(dim)[metric].agg(n="size", r="mean")
        g["w"] = g["n"] / g["n"].sum()  # segment share
        return g

    j = summarise(base).add_suffix("_0").join(
        summarise(cur).add_suffix("_1"), how="outer"
    ).fillna(0)
    overall_0 = base[metric].mean()

   

    # rate effect: the segment's own rate changed
    j["rate_effect"] = (j["r_1"] - j["r_0"]) * (j["w_0"] + j["w_1"]) / 2
    # mix effect: the segment's share changed (relative to the baseline average)
    j["mix_effect"] = (j["w_1"] - j["w_0"]) * ((j["r_0"] + j["r_1"]) / 2 - overall_0)
    j["contribution"] = j["rate_effect"] + j["mix_effect"]

    j = j.reset_index().rename(columns={dim: "segment"})
    j["dimension"] = dim
    return j[["dimension", "segment", "w_0", "w_1", "r_0", "r_1",
              "rate_effect", "mix_effect", "contribution"]]


def run_rca(df, base_month, cur_month, dims=DIMENSIONS):
    """Run the analysis on every dimension and rank all segments by impact."""
    parts = [contribution_analysis(df, d, base_month, cur_month) for d in dims]
    out = pd.concat(parts, ignore_index=True)
    out["abs_contribution"] = out["contribution"].abs()
    return out.sort_values("abs_contribution", ascending=False).reset_index(drop=True)


def total_change(df, base_month, cur_month):
    b = df.loc[df["renewal_month"] == pd.Timestamp(base_month), "renewed"].mean()
    c = df.loc[df["renewal_month"] == pd.Timestamp(cur_month), "renewed"].mean()
    return c - b


def narrate(df, base_month, cur_month):
    """Plain-English summary of the biggest driver."""
    res = run_rca(df, base_month, cur_month)
    delta = total_change(df, base_month, cur_month)
    top = res.iloc[0]
    share = top["contribution"] / delta if delta else float("nan")
    b = pd.Timestamp(base_month).strftime("%b %Y")
    c = pd.Timestamp(cur_month).strftime("%b %Y")
    return (
        f"Renewal rate moved {delta * 100:+.1f} pts ({b} → {c}). "
        f"Biggest single driver: **{top['dimension']} = {top['segment']}**, "
        f"explaining {share:.0%} of the move "
        f"(rate effect {top['rate_effect'] * 100:+.1f} pts, "
        f"mix effect {top['mix_effect'] * 100:+.1f} pts)."
    )
