# Discount Bond Database

Source for the [Discount Bond Database](https://discount-bond-data.org) website.

The database provides daily zero-coupon government yield curve estimates for six markets:
the United States, Germany, Japan, the United Kingdom, Canada and Switzerland. Curves are
estimated with Kernel Ridge Regression (KR) and, for the five non-U.S. markets, with KR-T, a
transfer-learning extension that carries information from the U.S. Treasury market through
foreign exchange. Discount bond returns, term structure factors and bond market condition
measures are also published for the United States.

The data files are hosted separately; the website links to them and documents the file
format, the sample construction and the conventions.

## Citation

> Filipovic, D., M. Pelger, and Y. Ye (2026). Stripping the Discount Curve - A Robust Machine
> Learning Approach. *Management Science* 72(9), 8057-8120.
> [doi:10.1287/mnsc.2023.01401](https://doi.org/10.1287/mnsc.2023.01401)

> Filipovic, D., M. Pelger, and Y. Ye (2026). Shrinking the Term Structure. *Review of
> Finance*, advance article.
> [doi:10.1093/rof/rfag033](https://doi.org/10.1093/rof/rfag033)

> Filipovic, D., M. Pelger, and R. Wang (2026). Stripping Discount Curves Across Currencies:
> Transfer Learning from US Treasuries. Working paper.
> [SSRN 7092381](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=7092381)

BibTeX entries are on the [website](https://discount-bond-data.org/methodology.html#cite).

## Contact

<mpelger@stanford.edu>
