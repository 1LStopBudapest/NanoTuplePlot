import matplotlib.pyplot as plt
import numpy as np


x = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
y = [0.09226003751059432, 0.13930265636252742, 0.17953840536408786, 0.2210312147528258, 0.271896025484962, 0.31982631559878655, 0.35115307100366744, 0.3689103358456043, 0.38630563036587007, 0.4113201701157255]

plt.title("Signal efficiency vs BR")
plt.xlabel("BR")
plt.ylabel("Signal efficiency (%)")
plt.legend(['mstop=300 mX0=280']) 

plt.scatter(x, y)
plt.savefig("plot.png")