from phc.explore.imports import has_ipywidgets, has_ipython
from phc.explore.view.main import MainView


class Explore:
    @staticmethod
    def start(shared_auth: bool = True, **kwargs):
        if has_ipywidgets is False:
            raise ValueError("ipywidgets is required for the explore module.")

        if has_ipython is False:
            raise ValueError("IPython is required for the explore module.")

        return MainView(shared_auth=shared_auth, **kwargs).widget()


__all__ = ["Explore"]
