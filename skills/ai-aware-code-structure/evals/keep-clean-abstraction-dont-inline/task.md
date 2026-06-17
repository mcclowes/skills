# Should a clean, tested pricing function be inlined?

Review question. We have pricing/calculatePrice.ts — a pure function, ~120 lines, fully typed inputs and outputs, with its own calculatePrice.test.ts. It's imported by 6 different call sites. A teammate wants to inline it back into the main CheckoutSummary component 'so Claude sees the whole pricing flow in one place when it's editing checkout.' We use AI assistants a lot. Is inlining a good move here?
