"""Build fixed, reproducible practice data. Run: python3 build-bank.py.
Each question family belongs to ONE new set. No runtime question generation.
The five cases per family use different numerical evidence, not copied stems.
"""
import json, math, random
from pathlib import Path

SOURCES = {
 'stats': ['NIST: statistical measures', 'https://www.itl.nist.gov/div898/handbook/eda/section3/eda35.htm'],
 'msa': ['NIST: measurement systems', 'https://www.itl.nist.gov/div898/handbook/mpc/mpc.htm'],
 'cap': ['NIST: process capability', 'https://www.itl.nist.gov/div898/handbook/pmc/section1/pmc16.htm'],
 'prob': ['NIST: probability distributions', 'https://www.itl.nist.gov/div898/handbook/eda/section3/eda366.htm'],
 'test': ['NIST: comparisons and inference', 'https://www.itl.nist.gov/div898/handbook/prc/prc.htm'],
 'reg': ['NIST: process modeling', 'https://www.itl.nist.gov/div898/handbook/pmd/pmd.htm'],
 'doe': ['NIST: experiment design', 'https://www.itl.nist.gov/div898/handbook/pri/pri.htm'],
 'spc': ['NIST: process monitoring', 'https://www.itl.nist.gov/div898/handbook/pmc/pmc.htm'],
 'lean': ['ASQ: Lean methods', 'https://asq.org/quality-resources/lean'],
 'bok': ['IASSC: Black Belt body of knowledge', 'https://iassc.org/body-of-knowledge/black-belt-body-of-knowledge/'],
}
sets = [dict(id=f'set-{i+2}', title=t, description=d, questions=[]) for i,(t,d) in enumerate([
 ('Measurement', '150 questions · Data, measurement systems, probability, and capability'),
 ('Analysis', '150 questions · Inference, hypothesis tests, ANOVA, and regression'),
 ('Experiments', '150 questions · Factorial designs, effects, models, and experimental error'),
 ('Process control', '150 questions · Control limits, chart signals, subgroups, and response plans'),
 ('Lean and Define', '150 questions · Lean flow, project benefits, Six Sigma metrics, and FMEA'),
])]

def fmt(x):
    if isinstance(x,str): return x
    return f'{x:.4f}'.rstrip('0').rstrip('.') if x else '0'

def add(tab,family,case,section,q,answer,wrong,e,source):
    opts=[fmt(answer)]+[fmt(x) for x in wrong]
    assert len(opts)==4 and len(set(opts))==4, (family,case,opts)
    # Fixed shuffle, never changes a saved answer's meaning.
    rng=random.Random(f'{tab}-{family}-{case}')
    rng.shuffle(opts)
    item=dict(id=f'S{tab+2}-{family:02d}-{case}',s=section,q=q,o=opts,a=opts.index(fmt(answer)),e=e,source=source,family=f'{tab}:{family}')
    sets[tab]['questions'].append(item)

def num(tab,fam,k,section,q,v,e,source,step=None):
    v=round(v,4)
    step=step or (max(1, round(abs(v)*.2)) if float(v).is_integer() else max(abs(v)*.2, .1))
    # Distractors are all distinct at displayed precision.
    wrong=[round(v+step,4),round(v+2*step,4),round(v+3*step,4)]
    if v>3*step: wrong=[round(v-step,4),round(v+step,4),round(v+2*step,4)]
    add(tab,fam,k,section,q+' Round to four decimal places if needed.',v,wrong,e+f' Result: {fmt(v)}.',source)

for k in range(1,6):
    def m(f,q,v,e,src='stats',step=None): num(0,f,k,'Measure',q,v,e,src,step)
    b=10*k
    m(1,f'Five cycle times are {b+1}, {b+2}, {b+3}, {b+4}, and {b+10} minutes. What is their arithmetic mean in minutes?',b+4,'Add all five cycle times, then divide by 5.')
    m(2,f'Six sorted queue times are {b}, {b+2}, {b+5}, {b+9}, {b+10}, and {b+14} seconds. What is their median in seconds?',b+7,'For six values, average the third and fourth observations.')
    m(3,f'Five batch weights are {b}, {b+3}, {b+8}, {b+2}, and {b+5} kg. What is the range in kg?',8,'The range is the maximum minus the minimum.',step=1)
    m(4,f'A random sample of {k+5} measurements has a sum of squared deviations from its sample mean of {(k+4)*(k+2)}. What is its unbiased sample variance?',k+2,'Sample variance divides the sum of squared deviations by n − 1.')
    m(5,f'A measurement study reports variance {(k+2)**2} square micrometres. What is the corresponding standard deviation in micrometres?',k+2,'Standard deviation is the positive square root of variance.')
    m(6,f'A delivery process has a positive mean of {20*k} hours and standard deviation {k+1} hours. What is its coefficient of variation, expressed as a percentage?',100*(k+1)/(20*k),'CV = 100 × standard deviation / mean.')
    m(7,f'A sample of {k*10} orders has mean handling time {20+k} minutes; another sample of {k*20} orders has mean {29+k} minutes. What is the combined mean in minutes?',26+k,'Use the sample sizes as weights: sum(n × mean) / sum(n).')
    m(8,f'A calibration standard is {50+k} mm. The mean of repeated readings is {50+k+.2*k} mm. What is the signed measurement bias in mm?',.2*k,'Bias = mean reading − reference value.','msa')
    m(9,f'Independent repeatability and reproducibility variance components are {k*k} and {(k+1)**2}. What is the total gage R&R standard deviation?',math.sqrt(k*k+(k+1)**2),'Add independent variance components, then take the square root.','msa')
    m(10,f'An independent measurement-error component has variance {k+1}; the total observed variance is {10*(k+1)}. What percentage of observed variance comes from measurement error?',10,'Percentage contribution = 100 × measurement variance / observed variance. This is a variance percentage, not a study-variation percentage.','msa',step=5)
    m(11,f'A gage standard deviation is {k/10} mm and the tolerance width is {k+3} mm. Using a 6-sigma study width, what is precision-to-tolerance as a percentage?',100*6*(k/10)/(k+3),'P/T (%) = 100 × 6 × gage standard deviation / tolerance width.','msa')
    m(12,f'Two inspectors agree on {80+k*3} of 100 independently rated items. What is their observed agreement percentage?',80+k*3,'Observed agreement = 100 × agreements / items rated.','msa',step=1)
    m(13,f'An attribute study has observed agreement {(.7+.04*k):.2f} and chance agreement 0.50. What is Cohen’s kappa?',((.7+.04*k)-.5)/.5,'Kappa = (observed agreement − chance agreement) / (1 − chance agreement).','msa')
    m(14,f'Of {40+10*k} truly defective parts, an inspector accepts {k+2}. What is the false-accept percentage among the truly defective parts?',100*(k+2)/(40+10*k),'Divide accepted defective parts by all truly defective parts, then multiply by 100.','msa')
    m(15,f'Of {100+20*k} truly conforming parts, an inspector rejects {k+3}. What is the false-reject percentage among the truly conforming parts?',100*(k+3)/(100+20*k),'Divide rejected conforming parts by all truly conforming parts, then multiply by 100.','msa')
    m(16,f'A stable normal process has USL {100+6*k}, LSL 100, and within-process sigma {k/2}. What is its potential capability index Cp?',2,'Cp = (USL − LSL) / (6 × within-process sigma).','cap',step=.25)
    m(17,f'A stable normal process has LSL 10, USL 40, mean {20+k}, and within-process sigma 2. What is Cpk?',min(40-20-k,20+k-10)/6,'Cpk is the smaller of (USL − mean)/(3σ) and (mean − LSL)/(3σ).','cap')
    m(18,f'A normal process has tolerance width {24+6*k} and overall standard deviation 3. What is Pp, using the overall rather than within-subgroup estimate?',(24+6*k)/18,'Pp = tolerance width / (6 × overall standard deviation).','cap')
    m(19,f'A process has USL 100, LSL 70, mean {92+k}, and overall standard deviation 2. What is Ppk?',(8-k)/6,'Ppk uses the nearest specification distance divided by three overall standard deviations.','cap')
    m(20,f'A normal characteristic has mean {100+k} and sigma 4. What is the z-score of a value {100+k+2*k}?',k/2,'z = (value − mean) / sigma.','prob')
    m(21,f'A binomial count has {20+10*k} independent trials and failure probability 0.10 on each trial. What is the expected failure count?',(20+10*k)*.1,'The binomial mean is n × p.','prob')
    m(22,f'A binomial count has {40+10*k} independent trials, each with defect probability 0.20. What is the count variance?',(40+10*k)*.2*.8,'Binomial variance = n × p × (1 − p).','prob')
    m(23,f'A sample has {k+2} independent items, each defective with probability 0.10. What is the probability that none is defective?',.9**(k+2),'For independent items, multiply the conforming probability 0.9 once for each item.','prob')
    m(24,f'A sample contains {k+3} independent items, each defective with probability 0.05. What is the probability of at least one defective item?',1-.95**(k+3),'Use the complement: 1 − probability that all items conform.','prob')
    m(25,f'Defects follow a Poisson process with mean {k/2} per panel. What is the probability of zero defects on a panel?',math.exp(-k/2),'For a Poisson count, P(X = 0) = exp(−mean).','prob')
    m(26,f'A Poisson process averages {k+1} calls per minute. What is the expected count during 3 minutes?',3*(k+1),'Multiply the constant rate by the observation duration.','prob')
    m(27,f'Waiting time is exponential with mean {k+2} minutes. What is the probability of waiting longer than 4 minutes?',math.exp(-4/(k+2)),'For exponential waiting time with mean m, P(T > t) = exp(−t/m).','prob')
    m(28,f'A normal process has mean {50+k} and sigma 2. What measurement lies {k/2} standard deviations below the mean?',50,'Use x = mean − z × sigma.','prob',step=2)
    m(29,f'A batch has 100 items. Of these, {20+k} have a scratch, {10+k} have a dent, and {k+2} have both. What is the probability that a randomly selected item has at least one of these defects?',(28+k)/100,'P(A or B) = P(A) + P(B) − P(A and B).','prob')
    m(30,f'Of {30+5*k} urgent orders, {k+4} are late. What is the conditional probability that an order is late, given that it is urgent?',(k+4)/(30+5*k),'Restrict the denominator to urgent orders because the condition is already known.','prob')

for k in range(1,6):
    def a(f,q,v,e,src='test',step=None): num(1,f,k,'Analyze',q,v,e,src,step)
    n=(k+3)**2
    a(1,f'For {n} independent observations with sample standard deviation {2*(k+3)}, what is the estimated standard error of the sample mean?',2,'Standard error of the mean = s / square root of n.',step=.25)
    a(2,f'A normal population has known sigma {k+2}. A sample of 25 has mean {100+k}. What is the margin of error for a 95% mean interval using z = 1.96?',1.96*(k+2)/5,'Margin = z × sigma / square root of n.')
    a(3,f'A mean estimate is {30+k}, its standard error is 1.5, and the specified two-sided critical t value is 2.10. What is the lower confidence bound?',30+k-2.1*1.5,'Lower bound = estimate − critical value × standard error.')
    a(4,f'A mean estimate is {40+k}, its standard error is 2, and the specified critical t value is 2.20. What is the upper confidence bound?',40+k+4.4,'Upper bound = estimate + critical value × standard error.')
    a(5,f'Plan a normal-mean study with known sigma {k+3}, desired margin 1, and z = 1.96. What minimum integer sample size does the usual formula require?',math.ceil((1.96*(k+3))**2),'Compute (z × sigma / margin)² and round upward to a whole observation.',step=1)
    a(6,f'A valid mean-interval design uses n = {25*k}. With the same variance and confidence level, what n gives half the margin of error?',100*k,'Margin is proportional to 1/√n. Halving it requires four times as many observations.')
    a(7,f'A one-sample t-test uses mean {50+k}, null mean 50, sample standard deviation 5, and n = 25. What is t?',k,'t = (sample mean − null mean) / (s/√n).')
    a(8,f'A one-sample t-test uses {10+3*k} independent normal observations. How many error degrees of freedom does its t statistic have?',9+3*k,'A one-sample t statistic has n − 1 degrees of freedom.',step=1)
    a(9,f'For {16+k} independent pairs, the mean before-minus-after difference is {2+k}, and its standard error is 0.5. What is the paired t statistic for zero mean difference?',2*(2+k),'Divide the mean difference by the standard error of the mean difference.')
    a(10,f'An equal-variance two-sample t-test uses independent groups of sizes {10+k} and {15+k}. What are its pooled error degrees of freedom?',23+2*k,'Pooled two-sample t degrees of freedom = n1 + n2 − 2.',step=1)
    a(11,f'Two independent sample means have standard errors {k} and {k+1}. What is the standard error of their difference?',math.sqrt(k*k+(k+1)**2),'For independent means, add their variances, then take the square root.')
    a(12,f'Two independent samples each have n = 10 and standard deviations {k+1} and {k+3}. What is the equal-variance pooled variance estimate?',((k+1)**2+(k+3)**2)/2,'Weight each sample variance by n − 1. Equal sizes give their average.')
    a(13,f'A test has Type II error probability {(.1+.05*k):.2f} at the specified alternative. What is its power as a percentage?',100*(.9-.05*k),'Power = 1 − beta, expressed here as a percentage.',step=5)
    a(14,f'Exactly {20*k} independent true null hypotheses are each tested at alpha = 0.05. What is the expected number of Type I errors?',k,'The expected count of false rejections is number of true nulls × alpha.')
    a(15,f'A family of {k+2} comparisons needs familywise alpha 0.05. What per-comparison alpha does the Bonferroni rule use?',.05/(k+2),'Divide the desired familywise alpha by the number of comparisons.')
    a(16,f'A contingency table has {k+2} rows and 3 columns, with no structural zeros. What are the chi-square independence-test degrees of freedom?',2*(k+1),'Degrees of freedom = (rows − 1) × (columns − 1).',step=1)
    a(17,f'In a contingency table, one row total is {20*k}, one column total is 40, and the grand total is 200. What is the expected count in their intersecting cell under independence?',4*k,'Expected cell count = row total × column total / grand total.')
    a(18,f'A Pearson chi-square cell has observed count {20+2*k} and expected count 20. What is this cell’s contribution to the statistic?',(2*k)**2/20,'Cell contribution = (observed − expected)² / expected.')
    a(19,f'A goodness-of-fit test has {k+4} categories and estimates one distribution parameter from the data. Assuming adequate expected counts, what are its degrees of freedom?',k+2,'Degrees of freedom = categories − 1 − number of parameters estimated.',step=1)
    a(20,f'A one-way ANOVA compares {k+2} independent groups. What are its between-group degrees of freedom?',k+1,'Between-group degrees of freedom = number of groups − 1.',step=1)
    a(21,f'A one-way ANOVA has {30+6*k} observations spread over {k+2} groups. What are its within-group degrees of freedom?',28+5*k,'Within-group degrees of freedom = total observations − groups.',step=1)
    a(22,f'An ANOVA has between-group mean square {12+3*k} and error mean square 3. What is its F statistic?',4+k,'F = between-group mean square / error mean square.')
    a(23,f'A regression with an intercept has total sum of squares {100*k} and residual sum of squares {20*k}. What is R-squared?',.8,'R² = 1 − residual sum of squares / total sum of squares.','reg',step=.05)
    a(24,f'A fitted process model is y = {10+k} + {k+1}x. What is its prediction at x = 3?',10+k+3*(k+1),'Substitute x = 3 into the fitted equation.','reg')
    a(25,f'An observed response is {30+2*k}; the regression prediction is {25+k}. What is the residual?',5+k,'Residual = observed response − fitted response.','reg')
    a(26,f'A fitted linear model includes an intercept and {k+1} predictors, with n = {30+5*k}. What are the residual degrees of freedom?',28+4*k,'Residual degrees of freedom = observations − predictors − 1 for the intercept.','reg',step=1)
    a(27,f'A regression coefficient is {1+.5*k} and its estimated standard error is 0.5. What is the t statistic for a zero coefficient?',2+k,'Coefficient t statistic = estimate / its standard error.','reg')
    a(28,f'A predictor regressed on all other predictors has R-squared {(.2+.1*k):.1f}. What is its variance inflation factor?',1/(.8-.1*k),'VIF = 1 / (1 − auxiliary R²).','reg')
    a(29,f'A regression has residual sum of squares {12*(k+1)} and 12 residual degrees of freedom. What is its residual mean square?',k+1,'Residual mean square = residual sum of squares / residual degrees of freedom.','reg')
    a(30,f'A fitted simple regression with intercept has sample correlation {(-.5-.05*k):.2f}. What is R-squared?',(-.5-.05*k)**2,'For simple least-squares regression with an intercept, R² is the squared sample correlation.','reg')

for k in range(1,6):
    def d(f,q,v,e,step=None): num(2,f,k,'Improve',q,v,e,'doe',step)
    d(1,f'A full factorial uses {k+1} two-level factors and three independent replicates of every combination. How many total runs are required?',3*2**(k+1),'Total runs = replicates × 2 to the power of the number of factors.')
    d(2,f'A two-level factorial design has {k+3} factors. A model includes only the intercept and main effects. How many coefficients does it contain?',k+4,'Count one intercept plus one coefficient per two-level factor.',step=1)
    d(3,f'A full two-level factorial has {k+2} factors. How many treatment combinations put factor A at its high level?',2**(k+1),'In a balanced full factorial, half of all treatment combinations use A high.')
    d(4,f'A half fraction of a two-level design with {k+3} factors is replicated twice. How many runs are needed?',2**(k+3),'Runs = 2 × 2^(factor count − 1).')
    d(5,f'A quarter fraction of a two-level design with {k+4} factors uses no replication or center points. How many runs are needed?',2**(k+2),'A quarter fraction uses 2^k / 4 treatment combinations.')
    d(6,f'A screening design uses {8*k} factorial runs plus {k+2} center runs. What is the total number of runs?',9*k+2,'Add factorial and center runs.')
    d(7,f'A design has {k+3} factors. How many distinct two-factor interaction terms are possible?',math.comb(k+3,2),'Choose unordered pairs of factors: k(k − 1)/2.')
    d(8,f'A design has {k+3} factors. How many distinct three-factor interaction terms are possible?',math.comb(k+3,3),'Choose unordered triples of factors: k(k − 1)(k − 2)/6.')
    d(9,f'A full second-order response-surface model uses {k+1} quantitative factors. Including the intercept, how many coefficients are required?',1+2*(k+1)+math.comb(k+1,2),'Count 1 intercept, k linear terms, k squared terms, and k(k − 1)/2 interactions.')
    d(10,f'A {k+3}-factor two-level full factorial is run once. A saturated model includes every interaction. How many non-intercept effects does it estimate?',2**(k+3)-1,'There is one coefficient for each combination, including the intercept. Subtract one to count effects.')
    d(11,f'In a balanced two-level experiment, the mean response at A high is {40+3*k}, and the mean at A low is {30+k}. What is the main effect of A, using high minus low?',10+2*k,'The main effect is the high-level mean minus the low-level mean.')
    d(12,f'A two-level coded regression uses levels −1 and +1. The estimated main effect of B is {4+2*k}. What is the coefficient of B in the coded model?',2+k,'The difference between coded levels is 2, so the coded coefficient is effect / 2.')
    d(13,f'A coded model contains the term {k+1}A with A at −1 and +1, and no interaction involving A. What response change is predicted when A moves from low to high?',2*(k+1),'The factor changes by 2 coded units; multiply the coefficient by 2.')
    d(14,f'A physical temperature range runs from {100+10*k} to {140+10*k} °C. What temperature in °C corresponds to coded level zero?',120+10*k,'Coded zero is the midpoint of the low and high settings.')
    d(15,f'A factor has physical center {50+5*k} and half-range 10. What coded value corresponds to physical setting {55+5*k}?',.5,'Coded value = (physical setting − center) / half-range.',step=.25)
    d(16,f'A factor is coded as x = (temperature − {100+5*k})/20. What temperature corresponds to x = −1.5?',70+5*k,'Physical setting = center + coded value × half-range.')
    d(17,f'For a 2×2 experiment, responses at (A−,B−), (A+,B−), (A−,B+), (A+,B+) are {10+k}, {14+k}, {12+k}, {20+3*k}. What is the A main effect?',6+k,'Average the two A-high responses and subtract the average of the two A-low responses.')
    d(18,f'For a 2×2 experiment, responses in order (−,−), (+,−), (−,+), (+,+) are {20+k}, {22+k}, {26+k}, {32+3*k}. What is the B main effect?',8+k,'Average the two B-high responses and subtract the average of the two B-low responses.')
    d(19,f'For a 2×2 experiment, responses in order (−,−), (+,−), (−,+), (+,+) are {10+k}, {12+k}, {14+k}, {20+3*k}. What is the AB interaction effect in the usual two-level effect convention?',2+k,'AB effect = (y−− + y++ − y+− − y−+)/2. It is half the difference between the two simple A effects.')
    d(20,f'A fitted model is y = {20+k} + 3A − 2B + {k}AB. What is the fitted response at A = +1, B = −1?',25,'Substitute the coded values; AB = −1, so y = intercept + 3 + 2 − k.',step=2)
    d(21,f'A model is y = 10 + {k+1}A + 2B + 3AB. With B fixed at +1, what is the predicted high-minus-low effect of A?',2*(k+4),'At B = +1, the A slope is (k + 1) + 3; multiply that slope by the coded change of 2.')
    d(22,f'A quadratic response model is y = {20+k} − {2*(k+1)}x + x². At what x does the model attain its minimum?',k+1,'Set the derivative −2(k + 1) + 2x to zero. The positive quadratic coefficient gives a minimum.')
    d(23,f'A two-level experiment predicts mean response {30+k} at the center from a first-order model. The observed center mean is {34+2*k}. What is observed-minus-predicted center deviation?',4+k,'Subtract the first-order center prediction from the observed center mean. A deviation alone does not establish statistical significance.')
    d(24,f'An experiment has {k+3} distinct settings, with 3 independent replicate runs at each setting. What are the pure-error degrees of freedom?',2*(k+3),'Pure-error degrees of freedom = total runs − number of distinct settings.')
    d(25,f'A replicated regression experiment has {20+2*k} observations, {8+k} distinct settings, and 5 fitted coefficients. What are the lack-of-fit degrees of freedom?',3+k,'Lack-of-fit degrees of freedom = distinct settings − fitted coefficients.')
    d(26,f'A lack-of-fit test has lack-of-fit mean square {8+2*k} and pure-error mean square 2. What is its F statistic?',4+k,'F for lack of fit = lack-of-fit mean square / pure-error mean square.')
    d(27,f'A balanced experiment has total sum of squares {100+20*k} and error sum of squares {20+5*k}. What is the sum of squares explained by the fitted treatments?',80+15*k,'Explained sum of squares = total sum of squares − error sum of squares.')
    d(28,f'In a balanced orthogonal two-level design with {8*k} total runs, an estimated effect is 4. What is the sum of squares for that effect?',32*k,'For ±1 coding and balanced orthogonal runs, effect sum of squares = N × effect² / 4.')
    d(29,f'A randomized complete block experiment has {k+2} treatments and 4 blocks, one run per treatment in each block. What are the residual degrees of freedom for the additive model?',3*(k+1),'Residual degrees of freedom = (treatments − 1) × (blocks − 1).')
    d(30,f'A balanced experiment assigns {k+2} independent runs to each of two factor levels. Individual response variance is 9. What is the standard error of the high-minus-low mean difference?',math.sqrt(18/(k+2)),'The independent mean variances add: standard error = √(9/n + 9/n).')

for k in range(1,6):
    def c(f,q,v,e,step=None): num(3,f,k,'Control',q,v,e,'spc',step)
    c(1,f'An X-bar chart uses known sigma {k+1}, subgroup size 4, and center {50+k}. What is the three-sigma upper control limit?',50+k+3*(k+1)/2,'UCL = process mean + 3 × sigma / √n.')
    c(2,f'An X-bar chart uses known sigma {k+2}, subgroup size 9, and center {60+k}. What is the three-sigma lower control limit?',58,'LCL = process mean − 3 × sigma / √n.',step=2)
    c(3,f'For an X-bar/R chart, grand mean is {40+k}, average range is {k+2}, and A2 = 0.577. What is the X-bar upper control limit?',40+k+.577*(k+2),'X-bar UCL = grand mean + A2 × average range.')
    c(4,f'For an R chart, average range is {k+2} and D4 = 2.114. What is its upper control limit?',2.114*(k+2),'Range UCL = D4 × average range.')
    c(5,f'For an R chart, average range is {10+k} and the supplied D3 is 0.223. What is its lower control limit?',.223*(10+k),'Range LCL = D3 × average range.')
    c(6,f'An individuals chart has mean {100+k}, average moving range {k+1}, and d2 = 1.128 for ranges of two. What is its estimated process sigma?',(k+1)/1.128,'Estimate sigma as average moving range / d2.')
    c(7,f'An individuals chart has mean {30+k} and estimated sigma {k/2}. What is its three-sigma upper limit?',30+2.5*k,'Individuals UCL = mean + 3 × estimated sigma.')
    c(8,f'Two successive individual readings are {20+k} and {25+2*k}. What is their moving range?',5+k,'A moving range of two is the absolute difference between successive readings.')
    c(9,f'An S chart uses average subgroup standard deviation {k+1} and B4 = 2.089. What is its upper control limit?',2.089*(k+1),'S-chart UCL = B4 × average subgroup standard deviation.')
    c(10,f'For an X-bar/S chart, grand mean is {80+k}, average s is {k+1}, and A3 = 1.427. What is the X-bar lower control limit?',80+k-1.427*(k+1),'X-bar LCL = grand mean − A3 × average subgroup standard deviation.')
    c(11,f'A p-chart baseline pools {10+k} defective items across {500+100*k} inspected items. What is its center line?',(10+k)/(500+100*k),'Pool all defective items and divide by all inspected items; do not average subgroup proportions without weights.')
    c(12,f'A p chart has baseline p = 0.04 and the next sample size is {100*k}. What is the three-sigma upper limit for this sample?',.04+3*math.sqrt(.04*.96/(100*k)),'p-chart UCL = p-bar + 3√[p-bar(1 − p-bar)/n].')
    c(13,f'A p chart has baseline p = 0.01 and subgroup size {10*k}. The formula gives a negative lower limit. What lower limit is plotted?',0,'A proportion cannot be negative; truncate the calculated lower limit to zero.',step=.01)
    c(14,f'An np chart uses constant subgroup size {100*k} and baseline defective proportion 0.03. What is the center line in defective items?',3*k,'np center line = n × p-bar.')
    c(15,f'An np chart uses n = {100*k} and baseline p = 0.05. What is the three-sigma upper control limit in count units?',5*k+3*math.sqrt(100*k*.05*.95),'np UCL = np-bar + 3√[np-bar(1 − p-bar)]. Leave the statistical limit unrounded except as requested.')
    c(16,f'A p-chart data set contains two subgroups of sizes {100*k} and {200*k}, with 5 and 10 defective items respectively. What pooled defective fraction should be used?',15/(300*k),'Pool the defective counts and divide by the sum of inspected counts.')
    c(17,f'A constant-size np chart has subgroup size {200*k} and np center line {4*k}. What is the equivalent p-chart center line?',.02,'Divide the expected defective count by subgroup size.',step=.005)
    c(18,f'A u-chart baseline records {100+20*k} defects across {50+5*k} equal opportunity units. What is its center line in defects per unit?',(100+20*k)/(50+5*k),'u-bar = pooled defects / pooled opportunity units.')
    c(19,f'A u chart has baseline 2 defects per unit. The next sample covers {k+3} units. What is the three-sigma upper limit in defects per unit?',2+3*math.sqrt(2/(k+3)),'u UCL = u-bar + 3√(u-bar/n).')
    c(20,f'A u chart has baseline 4 defects per unit. The next sample covers {10+k} units. What is the three-sigma lower limit in defects per unit?',4-3*math.sqrt(4/(10+k)),'u LCL = max(0, u-bar − 3√(u-bar/n)).')
    c(21,f'An EWMA uses lambda 0.20, previous smoothed value {50+k}, and current observation {60+2*k}. What is the new smoothed value?',.2*(60+2*k)+.8*(50+k),'EWMA = lambda × current observation + (1 − lambda) × previous EWMA.')
    c(22,f'An EWMA of independent individual observations has sigma {k+1} and lambda 0.20. What is its limiting standard deviation?',(k+1)*math.sqrt(.2/1.8),'Limiting EWMA sigma = process sigma × √[lambda/(2 − lambda)].')
    c(23,f'An upper one-sided CUSUM uses Cnew = max(0, Cold + x − target − K). With Cold = {k}, x = {12+k}, target = 10, and K = 1, what is Cnew?',1+2*k,'Insert the stated values into the one-sided CUSUM recursion.')
    c(24,f'An in-control chart has independent per-point false-alarm probability {(.01*k):.2f}. What is its in-control average run length?',100/k,'For independent signals with constant probability alpha, ARL = 1/alpha.')
    c(25,f'After a fixed process shift, a chart has independent detection probability {(.1*k):.1f} per sample. What is the average number of samples to a signal?',10/k,'A geometric waiting time with detection probability p has mean 1/p.')
    c(26,f'A chart takes a sample every {k+1} minutes and has ARL 8 for a specified shift. Using sampling interval × ARL, what is the average time to signal in minutes?',8*(k+1),'Multiply the stated sampling interval by the average run length.')
    c(27,f'An X-bar chart uses known sigma 4 and subgroup size {4*k}. Keeping sigma fixed, what is the ratio of the new control-limit half-width to the old half-width if subgroup size becomes {16*k}?',.5,'The limit half-width is proportional to 1/√n. Quadrupling n halves the width.',step=.1)
    c(28,f'The subgroup means for three equal-size rational subgroups are {10+k}, {14+k}, and {18+k}. What is their X-bar chart grand mean?',14+k,'For equal-size subgroups, average the subgroup means.')
    c(29,f'Four rational subgroups have ranges {k}, {k+2}, {k+4}, and {k+6}. What is their R-chart center line?',k+3,'The R-chart center line is the arithmetic mean of the subgroup ranges.')
    c(30,f'A control rule signals when at least 2 of 3 consecutive standardized points exceed +2 sigma. The last three values are 2.1, {2.2+.1*k:.1f}, and 0.5. How many of these three points exceed +2 sigma?',2,'The first two values exceed +2; the third does not. This meets the specified 2-of-3 signal rule.',step=1)

for k in range(1,6):
    def l(f,q,v,e,src='lean',step=None): num(4,f,k,'Improve' if f<16 else 'Define',q,v,e,src,step)
    l(1,f'A stable flow has average WIP {40+10*k} orders and throughput 10 orders/hour. By Little’s law, what is average flow time in hours?',4+k,'Flow time = average WIP / average throughput. Use consistent system boundaries and units.')
    l(2,f'A stable service process has throughput {5+k} cases/hour and average flow time 3 hours. What average WIP does Little’s law predict?',3*(5+k),'Average WIP = throughput × average flow time.')
    l(3,f'A stable process holds {100+20*k} units of average WIP and average flow time 4 hours. What is its average throughput in units/hour?',25+5*k,'Throughput = average WIP / average flow time.')
    l(4,f'An order spends {10+k} minutes in value-added work and {100+10*k} minutes in total elapsed lead time. What is process cycle efficiency as a percentage?',10,'Process cycle efficiency = 100 × value-added time / total lead time.',step=2)
    l(5,f'A line’s three serial stations have cycle times {20+k}, {30+k}, and {25+k} seconds/unit. Ignoring downtime and assuming adequate buffers, what is the line capacity in units/hour?',3600/(30+k),'The slowest station limits capacity. Divide 3,600 seconds/hour by its cycle time.')
    l(6,f'A line has total work content {180+30*k} seconds/unit and takt time 60 seconds/unit. What is the theoretical minimum integer number of stations?',math.ceil((180+30*k)/60),'Divide total work content by takt time and round upward. Precedence constraints may require more stations.',step=1)
    l(7,f'A line has 5 stations, cycle time 60 seconds, and total work content {200+10*k} seconds/unit. What is line-balance efficiency as a percentage?',100*(200+10*k)/300,'Balance efficiency = 100 × total work content / (station count × line cycle time).')
    l(8,f'A process completes {500+100*k} units with {10+5*k} total defects. What is DPU?',(10+5*k)/(500+100*k),'DPU = total defects / total units. A unit can contain more than one defect.','bok')
    l(9,f'A process inspects {1000+100*k} units, with 4 defined defect opportunities per unit, and records {20+4*k} defects. What is DPMO?',(20+4*k)/((1000+100*k)*4)*1e6,'DPMO = defects / (units × opportunities per unit) × 1,000,000.','bok')
    l(10,f'Of {500+100*k} units entering a step, {25+5*k} need rework and all others pass on their first attempt. What is first-time yield as a percentage?',95,'First-time yield excludes all units that need rework: 100 × first-pass good / input.','bok',step=1)
    l(11,f'Two consecutive steps have first-time yields 0.90 and {(.80+.02*k):.2f}, where each step’s yield is conditional on reaching that step. What is rolled throughput yield as a percentage?',100*.9*(.8+.02*k),'Multiply the conditional first-time yields, then convert to a percentage.','bok')
    l(12,f'A kanban calculation uses demand {20+5*k} units/hour, replenishment lead time 2 hours, safety factor 0.10, and container size 10 units. What minimum integer number of containers is required?',math.ceil((20+5*k)*2*1.1/10),'Containers = demand rate × lead time × (1 + safety factor) / container size, rounded upward.',step=1)
    l(13,f'A setup takes {60+5*k} minutes before improvement and {30+2*k} minutes after improvement. What is the percentage reduction?',100*(30+3*k)/(60+5*k),'Percent reduction = 100 × (old time − new time) / old time.')
    l(14,f'Internal setup contains {30+k} minutes of work. A verified change moves {10+k} minutes to external setup without changing the remaining work. What machine-stopped setup time remains?',20,'Only work that still requires the stopped machine contributes to the revised internal setup duration.',step=2)
    l(15,f'A work cell’s walking time falls from {12+k} to 5 minutes per cycle. It completes 20 cycles/day. How many walking minutes per day are removed?',20*(7+k),'Daily time removed = reduction per cycle × daily cycles.')
    l(16,f'An improvement avoids {100+20*k} scrap units/month at a variable cost of 5 currency units each, but adds 100 currency units/month in upkeep. What is the net monthly cost reduction?',400+100*k,'Net reduction = avoided scrap cost − added recurring upkeep.','bok')
    l(17,f'A project has a one-time cost of {10000+2000*k} and equal net monthly savings of 2000. Ignoring discounting, what is simple payback in months?',5+k,'Simple payback = initial cost / periodic net savings.','bok')
    l(18,f'An improvement produces annual benefits of {20000+5000*k} and annual costs of 10000. Using ROI = (benefits − costs)/costs, what is ROI as a percentage?',100+50*k,'Use the ROI definition given in the question and multiply by 100.','bok')
    l(19,f'A project costs 1000 now and returns {1200+100*k} exactly one year later. At a 10% annual discount rate, what is net present value?',(1200+100*k)/1.1-1000,'Discount the single future cash flow by 1.10 and subtract the time-zero investment.','bok')
    l(20,f'A future benefit of {1000+200*k} arrives in two years. At a 10% annual discount rate, what is its present value?',(1000+200*k)/(1.1**2),'Present value = future value / (1 + annual discount rate)^years.','bok')
    l(21,f'Expected annual benefit is {50000+5000*k}. The probability of obtaining it is 0.60, and otherwise benefit is zero. What is expected annual benefit?',.6*(50000+5000*k),'Expected value is the probability-weighted sum of the possible benefits.','bok')
    l(22,f'A quality-cost report lists prevention {100+k*10}, appraisal 200, internal failure {300+k*20}, and external failure 400. What is total failure cost?',700+20*k,'Total failure cost includes internal and external failures. Prevention and appraisal are excluded.','bok')
    l(23,f'A quality-cost report lists prevention {150+k*10}, appraisal {200+k*20}, internal failure 300, and external failure 400. What is total cost of quality?',1050+30*k,'Total cost of quality sums prevention, appraisal, internal failure, and external failure.','bok')
    l(24,f'Under traditional FMEA scoring, a failure has severity 8, occurrence {k+2}, and detection 4. What is its RPN?',32*(k+2),'RPN = severity × occurrence × detection. This number alone does not determine the appropriate action priority.','bok')
    l(25,f'An FMEA action leaves severity 9 and occurrence {k+1} unchanged, but reduces detection rating from 6 to 2. What is the absolute reduction in traditional RPN?',36*(k+1),'Subtract new S×O×D from old S×O×D; only D changes.','bok')
    l(26,f'A Pareto table lists {40+5*k} invoice errors, 25 address errors, and {35-5*k} quantity errors. What cumulative percentage is covered by the two largest categories?',65+5*k,'The invoice and address categories are the two largest. Their combined count divided by all 100 errors gives the cumulative percentage.','bok',step=5)
    l(27,f'A project reduces a late-delivery rate from {10+k}% to 4%. What is the reduction in percentage points?',6+k,'Subtract the new percentage from the old percentage. This is a percentage-point change, not a relative percent reduction.','bok',step=1)
    l(28,f'A project lowers error rate from {10+k}% to 5%. What is its relative percentage reduction?',100*(5+k)/(10+k),'Relative reduction = 100 × (old rate − new rate) / old rate.','bok')
    l(29,f'A verified improvement saves {k+2} minutes per transaction on 600 transactions/month. What monthly capacity is released in hours?',10*(k+2),'Multiply saved minutes by transactions and divide by 60. Released capacity is not automatically a cash saving.','bok')
    l(30,f'An ongoing control costs {100+20*k} per month and avoids expected failure costs of {300+50*k} per month. What is its net expected monthly benefit?',200+30*k,'Net benefit = expected avoided failure costs − recurring control cost.','bok')

SCOPE = [
 {**dict.fromkeys(range(1,8),'2.2.2'), **dict.fromkeys(range(8,16),'2.3.4'), **dict.fromkeys(range(16,20),'2.4.1'), **dict.fromkeys(range(20,31),'3.1.2')},
 {**dict.fromkeys(range(1,7),'3.2.1'), **dict.fromkeys(range(7,13),'3.4.1'), **dict.fromkeys(range(13,16),'3.3.3'), **dict.fromkeys(range(16,20),'3.5.8'), **dict.fromkeys(range(20,23),'3.4.3'), **dict.fromkeys(range(23,31),'4.2.2')},
 {**dict.fromkeys(range(1,4),'4.4.1'), 4:'4.5.1',5:'4.5.1', **dict.fromkeys(range(6,31),'4.4.2')},
 dict.fromkeys(range(1,31),'5.2.13'),
 {**dict.fromkeys(range(1,8),'2.1.2'), **dict.fromkeys(range(8,12),'1.2.5'),12:'5.1.2',13:'1.4.4',14:'1.4.4',15:'1.4.4', **dict.fromkeys(range(16,22),'1.3.3'),22:'1.2.3',23:'1.2.3',24:'2.1.4',25:'2.1.4',26:'1.2.4',27:'1.3.2',28:'1.3.2',29:'1.3.3',30:'5.3.1'},
]
for tab,s in enumerate(sets):
    for q in s['questions']:
        fam=int(q['family'].split(':')[1])
        q['scope']=SCOPE[tab][fam]
        q['s']={'1':'Define','2':'Measure','3':'Analyze','4':'Improve','5':'Control'}[q['scope'][0]]
# Keep topics grouped, with five distinct worked cases in each family.
for s in sets:
    s['questions'].sort(key=lambda q:q['id'])
    assert len(s['questions'])==150
assert len({q['q'] for s in sets for q in s['questions']})==750
Path('question-bank.json').write_text(json.dumps(dict(sources=SOURCES,sets=sets),ensure_ascii=False,indent=2)+'\n')
print('Built 750 questions: 150 question families, 5 numerical cases each, assigned to separate topic sets.')
# Preserve the original question literals and UI. Replace only the embedded bank.
import re
html=Path('index.html').read_text()
if '// BANK_START' in html:
    payload=json.dumps(dict(sources=SOURCES,sets=sets),ensure_ascii=False,separators=(',',':')).replace('</','<\\/')
    html=re.sub(r'(// BANK_START[^\n]*\n    const bank = ).*?(;\n    // BANK_END)',lambda m:m[1]+payload+m[2],html,flags=re.S)
    Path('index.html').write_text(html)
    Path('dist/index.html').write_text(html)
