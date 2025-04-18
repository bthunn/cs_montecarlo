from .OutlierMethods import OutlierStrategy, OutlierParams
from .InterpMethods import InterpStrategy

class ProcessorParams:
    def __init__(self, outlier_strategy:OutlierStrategy, outlier_params:OutlierParams,
                 interp_strategy:InterpStrategy):
        self.outlier_strategy = outlier_strategy
        self.outlier_params = outlier_params
        self.interp_strategy = interp_strategy
        pass

