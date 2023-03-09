import matplotlib.pyplot as plt
import squarify


def get_segmentation_map(df_rfm, col_name, seg_map):
    segments = df_rfm[col_name].value_counts().sort_values(ascending=False)
    fig = plt.gcf()
    ax = fig.add_subplot()
    fig.set_size_inches(16, 10)
    squarify.plot(
        sizes=segments,
        label=[label for label in seg_map.values()],
        color=[
            "#AFB6B5",
            "#F0819A",
            "#926717",
            "#F0F081",
            "#81D5F0",
            "#C78BE5",
            "#748E80",
            "#FAAF3A",
            "#7B8FE4",
            "#86E8C0",
        ],
        pad=False,
        bar_kwargs={"alpha": 1},
        text_kwargs={"fontsize": 15},
    )
    plt.title("Customer Segmentation Map", fontsize=20)
    plt.xlabel("Frequency", fontsize=18)
    plt.ylabel("Recency", fontsize=18)
    plt.show()
