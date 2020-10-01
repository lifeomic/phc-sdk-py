from phc.explore.imports import w


class NavigationButton:
    @staticmethod
    def toggle_left():
        return w.Button(icon="chevron-left", layout=dict(width="30px"))
