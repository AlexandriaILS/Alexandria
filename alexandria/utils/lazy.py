import operator
from typing import Any, Callable


class LazyObject:
    # Lightly modified code from
    # https://coderbook.com/python/2020/04/23/how-to-make-lazy-python.html
    _wrapped: Callable = None
    _is_init: bool = False

    def __init__(self, factory: Callable) -> None:
        # Assign using __dict__ to avoid the setattr method.
        self.__dict__["_factory"] = factory

    def _setup(self) -> None:
        self._wrapped = self._factory()
        self._is_init = True

    def new_method_proxy(func: Callable) -> Callable:
        """
        Deliberately trample on the local scope to inject functionality from
        the wrapped object.
        """

        def inner(self, *args: list[Any]) -> Any:
            if not self._is_init:
                self._setup()
            return func(self._wrapped, *args)

        return inner

    def __setattr__(self, name: str, value: Any) -> None:
        # These are special names that are on the LazyObject.
        # every other attribute should be on the wrapped object.
        if name in {"_is_init", "_wrapped"}:
            self.__dict__[name] = value
        else:
            if not self._is_init:
                self._setup()
            setattr(self._wrapped, name, value)

    def __delattr__(self, name: str) -> None:
        if name == "_wrapped":
            raise TypeError("can't delete _wrapped.")
        if not self._is_init:
            self._setup()
        delattr(self._wrapped, name)

    __getattr__ = new_method_proxy(getattr)
    __bytes__ = new_method_proxy(bytes)
    __str__ = new_method_proxy(str)
    __bool__ = new_method_proxy(bool)
    __dir__ = new_method_proxy(dir)
    __hash__ = new_method_proxy(hash)
    __class__ = property(new_method_proxy(operator.attrgetter("__class__")))
    __eq__ = new_method_proxy(operator.eq)
    __lt__ = new_method_proxy(operator.lt)
    __gt__ = new_method_proxy(operator.gt)
    __ne__ = new_method_proxy(operator.ne)
    __getitem__ = new_method_proxy(operator.getitem)
    __setitem__ = new_method_proxy(operator.setitem)
    __delitem__ = new_method_proxy(operator.delitem)
    __iter__ = new_method_proxy(iter)
    __len__ = new_method_proxy(len)
    __contains__ = new_method_proxy(operator.contains)
