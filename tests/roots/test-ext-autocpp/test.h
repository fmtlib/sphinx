// Not an apidoc

/* Not an apidoc */

/**
  Function `fun` description

  - item 1
  - item 2
 */
void fun();

/** A function template */
template <typename T>
void fun_template(T);

/** An invalid declaration */
bad_decl*();

/** A function with reference parameters */
void fun_ref(int& a, int &b);

/** A function with pointer parameters */
void fun_ptr(int* a, int *b);

/** A function with comments */
// before
void fun_with_comments(); // after

/** A function with a macro */
void fun_with_macro MACRO1 (MACRO2());

/** A function with a trailing return type. */
auto fun_with_trailing_return() -> int;

/** Class `cls` description */
class cls {};
