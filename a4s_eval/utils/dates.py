import pandas as pd


def get_date_batches(
    start_date: pd.Timestamp,
    end_date: pd.Timestamp,
    date_round: str,
    window: str,
    freq: str,
) -> list[tuple[pd.Timestamp, pd.Timestamp]]:
    start_date_round = start_date
    end_date_round = end_date
    if date_round:
        start_date_round = start_date.floor(date_round)
        end_date_round = end_date.ceil(date_round)

    date_ranges = pd.date_range(
        start_date_round, end_date_round, freq=freq
    )
    windows = date_ranges.to_series().add(pd.Timedelta(window))

    valid_batches = windows[windows <= end_date_round]

    return list(zip(date_ranges[: len(valid_batches)], valid_batches))


class DateIterator:
    def __init__(
        self,
        date_round: str,
        window: str,
        freq: str,
        df: pd.DataFrame,
        date_feature: str,
    ):
        self.start_date = df[date_feature].min()
        self.end_date = df[date_feature].max()
        self.date_round = date_round
        self.window = window
        self.freq = freq
        self.batches = get_date_batches(
            self.start_date, self.end_date, date_round, window, freq
        )
        self.index = 0
        self.df = df
        self.date_feature = date_feature

    def __iter__(self) -> "DateIterator":
        return self

    def __next__(self) -> tuple[pd.Timestamp, pd.DataFrame]:
        if self.index >= len(self.batches):
            raise StopIteration
        start, end = self.batches[self.index]
        self.index += 1
        return end, self.df[
            (self.df[self.date_feature] >= start) & (self.df[self.date_feature] < end)
        ].copy()
