from typing import Any, ClassVar, Iterator
from sympy.core.cache import cached_property
from sympy.core.expr import Expr
from sympy.core.function import AppliedUndef, Function
from sympy.core.relational import Equality
from sympy.core.symbol import Symbol
from sympy.series.order import Order

class ODEMatchError(NotImplementedError):
    ...


class SingleODEProblem:
    eq: Expr = ...
    func: AppliedUndef = ...
    sym: Symbol = ...
    _order: int = ...
    _eq_expanded: Expr = ...
    _eq_preprocessed: Expr = ...
    _eq_high_order_free = ...
    def __init__(self, eq, func, sym, prep=..., **kwargs) -> None:
        ...
    
    @cached_property
    def order(self) -> int:
        ...
    
    @cached_property
    def eq_preprocessed(self) -> Expr:
        ...
    
    @cached_property
    def eq_high_order_free(self) -> Expr:
        ...
    
    @cached_property
    def eq_expanded(self) -> Expr:
        ...
    
    def get_numbered_constants(self, num=..., start=..., prefix=...) -> list[Symbol]:
        ...
    
    def iter_numbered_constants(self, start=..., prefix=...) -> Iterator[Symbol]:
        ...
    
    @cached_property
    def is_autonomous(self) -> bool:
        ...
    
    def get_linear_coefficients(self, eq, func, order) -> dict[int, Any | Order] | None:
        ...
    


class SingleODESolver:
    hint: ClassVar[str]
    has_integral: ClassVar[bool]
    ode_problem: SingleODEProblem = ...
    _matched: bool | None = ...
    order: list | None = ...
    def __init__(self, ode_problem) -> None:
        ...
    
    def matches(self) -> bool:
        ...
    
    def get_general_solution(self, *, simplify: bool = ...) -> list[Equality]:
        ...
    


class SinglePatternODESolver(SingleODESolver):
    def wilds(self):
        ...
    
    def wilds_match(self) -> list[Any]:
        ...
    


class NthAlgebraic(SingleODESolver):
    hint = ...
    has_integral = ...
    _diffx_stored: dict[Symbol, type[Function]] = ...


class FirstExact(SinglePatternODESolver):
    hint = ...
    has_integral = ...
    order = ...


class FirstLinear(SinglePatternODESolver):
    hint = ...
    has_integral = ...
    order = ...


class AlmostLinear(SinglePatternODESolver):
    hint = ...
    has_integral = ...
    order = ...


class Bernoulli(SinglePatternODESolver):
    hint = ...
    has_integral = ...
    order = ...


class Factorable(SingleODESolver):
    hint = ...
    has_integral = ...


class RiccatiSpecial(SinglePatternODESolver):
    hint = ...
    has_integral = ...
    order = ...


class RationalRiccati(SinglePatternODESolver):
    has_integral = ...
    hint = ...
    order = ...


class SecondNonlinearAutonomousConserved(SinglePatternODESolver):
    hint = ...
    has_integral = ...
    order = ...


class Liouville(SinglePatternODESolver):
    hint = ...
    has_integral = ...
    order = ...


class Separable(SinglePatternODESolver):
    hint = ...
    has_integral = ...
    order = ...


class SeparableReduced(Separable):
    hint = ...
    has_integral = ...
    order = ...


class HomogeneousCoeffSubsDepDivIndep(SinglePatternODESolver):
    hint = ...
    has_integral = ...
    order = ...


class HomogeneousCoeffSubsIndepDivDep(SinglePatternODESolver):
    hint = ...
    has_integral = ...
    order = ...


class HomogeneousCoeffBest(HomogeneousCoeffSubsIndepDivDep, HomogeneousCoeffSubsDepDivIndep):
    hint = ...
    has_integral = ...
    order = ...


class LinearCoefficients(HomogeneousCoeffBest):
    hint = ...
    has_integral = ...
    order = ...


class NthOrderReducible(SingleODESolver):
    hint = ...
    has_integral = ...


class SecondHypergeometric(SingleODESolver):
    hint = ...
    has_integral = ...


class NthLinearConstantCoeffHomogeneous(SingleODESolver):
    hint = ...
    has_integral = ...


class NthLinearConstantCoeffVariationOfParameters(SingleODESolver):
    hint = ...
    has_integral = ...


class NthLinearConstantCoeffUndeterminedCoefficients(SingleODESolver):
    hint = ...
    has_integral = ...


class NthLinearEulerEqHomogeneous(SingleODESolver):
    hint = ...
    has_integral = ...


class NthLinearEulerEqNonhomogeneousVariationOfParameters(SingleODESolver):
    hint = ...
    has_integral = ...


class NthLinearEulerEqNonhomogeneousUndeterminedCoefficients(SingleODESolver):
    hint = ...
    has_integral = ...


class SecondLinearBessel(SingleODESolver):
    hint = ...
    has_integral = ...


class SecondLinearAiry(SingleODESolver):
    hint = ...
    has_integral = ...


class LieGroup(SingleODESolver):
    hint = ...
    has_integral = ...


solver_map = ...