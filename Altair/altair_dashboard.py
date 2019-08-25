import os
import sys

sys.path.insert(0, os.path.dirname(os.getcwd()))
import altair as alt
from load_data import load_data

alt.themes.enable("ggplot2")


def make_chart(df):
    brush = alt.selection_interval(encodings=["x"], empty="all")
    data = (
        alt.Chart(df)
            .properties(height=300, width=600)
            .transform_timeunit(month="yearmonth(OCCURRED_ON_DATE)")
    )

    offenses_base = data.properties(title="Offenses per Month").transform_aggregate(
        num_offenses="count()", groupby=["month"]
    )

    offenses_line = offenses_base.encode(
        x=alt.X("month:T", timeUnit="yearmonth", axis=alt.Axis(title=None)),
        y=alt.Y(
            "num_offenses:Q",
            scale=alt.Scale(zero=False),
            axis=alt.Axis(title="Monthly Offenses"),
        ),
        tooltip=[
            alt.Tooltip("month:T", title="Date"),
            alt.Tooltip("count()", title="Number of Offenses"),
        ],
    )

    offenses_mean = (
        offenses_base.mark_rule(strokeDash=[8, 3])
            .transform_filter(brush)
            .encode(
            y="mean(num_offenses):Q", size=alt.value(1.5), color=alt.value("#e26855")
        )
    )

    num_monthly_offenses = (
            offenses_line.mark_line(interpolate="monotone", color="#e26855").add_selection(
                brush
            )
            + offenses_line.mark_circle(color="black")
            + offenses_mean
    )

    shooting_base = data.properties(title="Monthly Shootings").transform_aggregate(
        number_of_shootings="sum(SHOOTING)", groupby=["month"]
    )

    shootings = shooting_base.mark_line(interpolate="monotone", color="#e26855").encode(
        x=alt.X("month:T", axis=alt.Axis(title=None)),
        y=alt.Y("number_of_shootings:Q", axis=alt.Axis(title="Shootings pr Month")),
        tooltip=[
            alt.Tooltip("number_of_shootings:Q", title="Number of Shootings"),
            alt.Tooltip("yearmonth(month)", title="Date"),
        ],
    )

    shootings_mean_line = (
        shooting_base.mark_rule(strokeDash=[8, 3])
            .transform_filter(brush)
            .encode(
            y="mean(number_of_shootings):Q",
            color=alt.value("#e26855"),
            size=alt.value(1.5),
        )
    )

    shootings_per_month = (
            shootings.add_selection(brush)
            + shootings.mark_circle(color="black")
            + shootings_mean_line
    )

    top10 = (
        data.properties(title="Top 10 Offense Code Groups")
            .transform_filter(brush)
            .transform_aggregate(count="count()", groupby=["OFFENSE_CODE_GROUP"])
            .transform_window(
            rank="rank(count)", sort=[alt.SortField("count", order="descending")]
        )
            .transform_filter(alt.datum.rank < 10)
            .mark_bar()
            .encode(
            y=alt.Y(
                "OFFENSE_CODE_GROUP:N",
                sort=alt.EncodingSortField(field="count", op="sum", order="descending"),
                title="Code Group",
            ),
            x="count:Q",
        )
    )

    labels = top10.mark_text(baseline="middle", align="left", dx=3).encode(
        text="count:Q"
    )
    top10_code_groups = labels + top10

    heatmap_base = (
        data.properties(title="Number of Offenses by Day and Hour")
            .transform_filter(brush)
            .transform_aggregate(num_offenses="count()", groupby=["HOUR", "DAY_OF_WEEK"])
            .encode(
            y=alt.Y(
                "DAY_OF_WEEK:O",
                title="Day of Week",
                sort=[
                    "Monday",
                    "Tuesday",
                    "Wednesday",
                    "Thursday",
                    "Friday",
                    "Saturday",
                    "Sunday",
                ],
            ),
            x=alt.X("HOUR:O", title="Hour of Day"),
            tooltip=[
                alt.Tooltip("DAY_OF_WEEK", title="Day of Week"),
                alt.Tooltip("HOUR", title="Hour of Day"),
                alt.Tooltip("num_offenses:Q", title="Number of Offenses"),
            ],
            color=alt.Color("num_offenses:Q", legend=None),
        )
    )

    heatmap = heatmap_base.mark_rect()
    heatmap_text = heatmap_base.mark_text(baseline="middle").encode(
        text="num_offenses:Q",
        color=alt.condition(
            alt.datum.num_offenses < 1000, alt.value("black"), alt.value("white")
        ),
    )
    day_hour_counts = heatmap + heatmap_text

    return (shootings_per_month | num_monthly_offenses) & (
            top10_code_groups | day_hour_counts
    )


if __name__ == '__main__':
    sample_data = load_data().query("YEAR == 2018").sample(10000)
    make_chart(sample_data).save('altair_dashboard.html')
