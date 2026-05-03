# Test Queries for `sample.pdf` (Lumora Labs Employee Handbook)

The sample PDF is a fictional 4-page company handbook. Use these queries to verify the agent's grounding and refusal behavior.

## Valid queries (answerable from the PDF)

| # | Query | Expected answer (gist) | Expected citation page |
|---|-------|------------------------|------------------------|
| 1 | Where is Lumora Labs headquartered, and when was it founded? | Headquartered in Bengaluru, India; founded in 2017 by Anika Rao and Marcus Belo. | p. 1 |
| 2 | How many days of paid annual leave do full-time employees receive, and how many days can carry over? | 24 days of paid annual leave per year; up to 10 unused days carry over. | p. 2 |
| 3 | What is the daily meal allowance for business travel within Europe? | 90 USD per day. | p. 2 |
| 4 | How is Tier 1 customer data required to be stored? | Encrypted at rest using AES-256, accessed only from company-managed devices. | p. 3 |
| 5 | When are formal performance review cycles held, and when are promotions evaluated? | Two cycles per year, in June and December; promotions are evaluated only during the December cycle. | p. 4 |

## Invalid / out-of-scope queries (must refuse)

| # | Query | Expected behavior |
|---|-------|-------------------|
| 1 | What is the current stock price of Apple Inc.? | `refused=True`, `citations=[]`, refusal message returned verbatim. |
| 2 | Write me a Python function that computes the Fibonacci sequence. | `refused=True`, `citations=[]`, refusal message returned verbatim. |
| 3 | Who won the 2024 FIFA World Cup? | `refused=True`, `citations=[]`, refusal message returned verbatim. |

## Multi-language bonus

The same five valid queries should also work when asked in another language (e.g., Hindi, Spanish, French) because the embedding model is multilingual. The agent detects the query language and instructs the LLM to respond in the same language. Example:

- Query (Spanish): "¿Cuántos días de licencia anual pagada reciben los empleados a tiempo completo?"
- Expected: Spanish response, citing p. 2, around "24 días".
