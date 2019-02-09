# changepoint

The changepoint module is an offline changepoint detection module. It's based on Twitter's Breakpoint algorithm (originally developed in R) which relies on "energy statistics." 

For a given segment, potential changepoints are ranked by their q-statistic (a function of the the size of the data on either side of the changepoint and the medians on either side.) The index with the highest q value is a candidate changepoint. Since no sampling distribution exist for q (that I'm aware of at least) the algorithm uses a permutation test for inference. This slows the algorithm down significantly, so a potential solution for this would be to test every other index instead of all indices.

A segment consists of all observations within two bounds, inclusive. For a candidate changepoint, the median of the observations on either side are recorded, as are the lengths of each segment. Call the medians $A$ and $B$ and the lengths $n$ and $m$. Then the $q$-statistic for that candidate is:
$q = \frac{n*m}{n+m} * (2*(A*B)^2)$ 


$x^2$

The original paper: 
(can't find it right now but I will!)

To do:
  1) re-parameterize the time index so from 0 to 1 for the bin search
  2) figure out why it sucks when tested on the daily fed funds rate
