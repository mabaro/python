import pandas as pd
import matplotlib.pyplot as plot

fig1 = plot.figure()
axis1 = fig1.add_subplot(111)

df = pd.read_csv("samples.csv")
df.head()

if len(df) == 0:
    print("No data")
    exit(0)


df2 = df.copy()
df2['temperature'] = df2['temperature'].transform(lambda x: x + 1.015*x)

xName = 'seconds'
yName = 'temperature'
plot.plot(xName, yName, data=df, color='green', marker='+', linewidth=1, markersize=5, label='line1')
plot.plot(xName, yName, data=df2, color='blue', marker='*', linewidth=1, markersize=5, label='line2')

plot.show()
#plot.savefig("sampledata.png")
# plot.savefig("myImagePDF.pdf", format="pdf", bbox_inches="tight")
