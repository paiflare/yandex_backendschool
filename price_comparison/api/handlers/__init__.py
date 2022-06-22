from price_comparison.api.handlers.delete import DeleteView
from price_comparison.api.handlers.imports import ImportsView
from price_comparison.api.handlers.nodes import NodesView

HANDLERS = (
    ImportsView,
    NodesView,
    DeleteView,
)
