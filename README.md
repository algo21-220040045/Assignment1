# Assignment1
  This paper I reproduced is related to factor investing. Its theme is how to choose good stocks from high-valued stocks in the market, so as to achieve a good stratification effect. This has a good guiding role in the current overheated market. The original paper selected stocks from the US market and verified the stability of this stratification effect from the perspective of econometric finance. I used a similar method in the A-share market to observe the effect of the backtest.
  
  The idea of the strategy:
  Use 8 standards related to fundamental indicators. If a stock meets this standard, one point is added, otherwise no point is added.
  In this way, at each time when the position is exchanged, the stock will be divided into 9 groups, each with a score of 0-8.
  The weighting method of the strategy is equal weight.
  Then select stocks with scores of 6, 7, and 8 to buy and hold.
  The time points for swapping positions are the end of April, the end of August and the end of October. Respectively correspond to the deadline for the financial statement announcement.  
  Index category Judgment condition：
    1.ROA is greater than the median of the primary industry in which the stock is located
    2.Operating cash flow/total assets are greater than the median of the primary industry
    3.Operating cash flow is greater than 0 and greater than net profit
    4.The variance of ROA in the past five years is smaller than the median of the first-tier industry
    5.The variance of the sales growth rate in the past five years is smaller than the median of the first-level industry
    6.R&D expenses are greater than the median of the primary industry
    7.Capital expenditure is greater than the median of the primary industry
    8.Advertising costs are greater than the median of the primary industry

The figure below is a comparison of the backtest net value of different groups.
![image](https://user-images.githubusercontent.com/80148045/111408658-90976700-8710-11eb-9fb1-8c47b0756760.png)

![image](https://user-images.githubusercontent.com/80148045/111404436-b8cf9780-8709-11eb-8d2a-f1993043b8cb.png)
The stock portfolio income is stable. Even in this pessimistic market environment after the Lunar New Year, a positive return of 4% was achieved.

![image](https://user-images.githubusercontent.com/80148045/111409341-ba9d5900-8711-11eb-8c1a-f1e007f1837d.png)
