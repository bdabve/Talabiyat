from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class StatisticsWidget(FigureCanvas):
    def __init__(self, parent=None):
        fig = Figure(figsize=(5, 4), dpi=100)
        self.axes = fig.add_subplot(111)
        super().__init__(fig)

    def plot_orders_by_status(self, orders_by_status):
        """
        Plot a bar chart for orders grouped by status.
        :param orders_by_status: Aggregated data of orders grouped by status.
        """
        statuses = []
        counts = []

        for entry in orders_by_status:
            statuses.append(entry["_id"])  # e.g., "pending", "confirmed"
            counts.append(entry["count"])

        self.axes.clear()
        self.axes.bar(statuses, counts, color="skyblue")
        self.axes.set_title("Orders by Status")
        self.axes.set_xlabel("Status")
        self.axes.set_ylabel("Number of Orders")
        self.draw()
