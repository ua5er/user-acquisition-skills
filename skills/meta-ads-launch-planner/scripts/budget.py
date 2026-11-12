import sys
cpa = float(sys.argv[1]) if len(sys.argv) > 1 else 38
for k in (0.7, 0.85, 1.0, 1.15, 1.3):
    c = cpa * k
    learn = c * 50 / 7
    print(f"CPA {c:6.2f} | learn/day {learn:7.0f} | @190: {190/c:4.1f}/day | @380: {380/c:4.1f}/day")
