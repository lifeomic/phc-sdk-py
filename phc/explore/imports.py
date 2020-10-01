try:
    import ipywidgets as w
except ImportError:
    has_ipywidgets = False
    from collections import namedtuple as Struct

    # Build mock module that contains at least the type definitions so that the
    # individual views can be imported
    ipywidgets = Struct(
        "ipywidgets",
        [
            "DOMWidget",
            "HTML",
            "Output",
            "Button",
            "VBox",
            "HBox",
            "Dropdown",
            "Label",
        ],
    )

    w = ipywidgets(None, None, None, None, None, None, None, None,)
else:
    has_ipywidgets = True

try:
    from IPython.display import display
    from IPython.core.getipython import get_ipython
except ImportError:
    has_ipython = False
    display = None
    get_ipython = None
else:
    has_ipython = True
