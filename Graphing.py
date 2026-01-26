import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# --------------------------------------------
# Example: replace these with your real arrays
# --------------------------------------------

data = pd.read_csv("CleanedDataBHA18.csv")

dataDrilling = data[data["Surface_GC_OnBottom(bool)"] == 1]
#data = data[data["Surface_GC_OnBottom(bool)"] == 0]
#data = dataDrilling[dataDrilling["Surface_GC_Rotating(bool)"] == 1]
data = dataDrilling[dataDrilling["Surface_GC_Sliding(bool)"] == 1]

maxrpm = data["Augmented RPM(RPM)"].max()
maxwob = data["Surface_Weight on Bit(klbs)"].max()
print(maxwob)
nwob = 5
nrpm = 10
rpm = np.arange(0,maxrpm,nrpm)   #x axis
wob = np.arange(10,maxwob,nwob)    #y axis


# Surface_Weight on Bit(klbs)
# Bit Box_ShYpeak(g)
# Surface_Top Drive RPM(RPM)

hfto = np.zeros((len(wob), len(rpm)))
hftoPercentage = np.zeros((len(wob), len(rpm)))

wobcounter = 10  # upper edge of first WOB bin
for y in range(len(wob)):           # loop over WOB bins
    rpmcounter = 10                 # reset RPM counter for each WOB row

    for x in range(len(rpm)):       # loop over RPM bins
        mask = (
            (data["Surface_Weight on Bit(klbs)"] < wobcounter) &
            (data["Surface_Weight on Bit(klbs)"] >= wobcounter - 10) &
            (data["Augmented RPM(RPM)"] < rpmcounter) &
            (data["Augmented RPM(RPM)"] >= rpmcounter - 10)
        )

        hfto[y, x] = data.loc[mask, "Bit Box_ShYpeak(g)"].mean()
        if len(data.loc[mask, "Bit Box_ShYpeak(g)"]) != 0:
            hftoPercentage[y,x] = (len(data.loc[mask, "Bit Box_ShYpeak(g)"])/len(data))*100
        else:
            hftoPercentage[y,x] = np.nan

        rpmcounter += nrpm            # move to next RPM bin

    wobcounter += nwob                # move to next WOB bin



    
# --------------------------------------------
# Plotting
# --------------------------------------------
fig, ax = plt.subplots(figsize=(8,4))

# Create a scatter grid (WOB on y, RPM on x)
RPM, WOB = np.meshgrid(rpm, wob)

scatter = ax.scatter(
    RPM.flatten(),
    WOB.flatten(),
    c=hfto.flatten(),
    cmap="RdYlGn_r",      # green->red like your image
    s=300,                # size of squares
    marker="s",           # square marker
    edgecolor="k",        # black outline like your figure
    linewidth=0.3
)

# Labels
ax.set_xlabel("Augmented RPM")
ax.set_ylabel("WOB [klbs]")
ax.set_title("HFTO Indicator")

# Colorbar
cbar = plt.colorbar(scatter, label="Mean Peak BitYShock (g's)")

plt.tight_layout()
plt.show()

# --------------------------------------------
# Plotting
# --------------------------------------------
fig, ax = plt.subplots(figsize=(8,4))

# Create a scatter grid (WOB on y, RPM on x)
RPM, WOB = np.meshgrid(rpm, wob)

scatter = ax.scatter(
    RPM.flatten(),
    WOB.flatten(),
    c=hftoPercentage.flatten(),
    cmap="RdYlGn_r",      # green->red like your image
    s=300,                # size of squares
    marker="s",           # square marker
    edgecolor="k",        # black outline like your figure
    linewidth=0.3
)

# Add text labels (float values) above each square
for x, y, val in zip(RPM.flatten(), WOB.flatten(), hftoPercentage.flatten()):
    ax.text(
        x, 
        y + 1,          # slight vertical offset so text is above the square
        f"{val:.2f}",   # format to 2 decimal places
        ha="center", 
        va="bottom",
        fontsize=6,     # smaller label to avoid clutter
        color="black"
    )


# Labels
ax.set_xlabel("Augmented RPM")
ax.set_ylabel("WOB [klbs]")
ax.set_title("Data Percentage")

# Colorbar
cbar = plt.colorbar(scatter, label="Data Percentage")

plt.tight_layout()
plt.show()