from climada.entity import Exposures
import matplotlib.pyplot as plt

# Load the exposure data
exposure = Exposures.from_hdf5('data/exposure/exposure_nigeria_worldpop_1.0km.hdf5')

# Basic info
print(f"Total exposure points: {len(exposure.gdf):,}")
print(f"Total value: {exposure.gdf['value'].sum():,.0f}")

# Plot the exposure
exposure.plot_scatter()
plt.title('Nigeria Population Exposure')
plt.savefig('data/exposure/nigeria_exposure_map.png', dpi=300, bbox_inches='tight')
print("Plot saved to: data/exposure/nigeria_exposure_map.png")
plt.show()

