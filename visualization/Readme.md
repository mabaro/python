# subplots https://matplotlib.org/stable/gallery/subplots_axes_and_figures/subplots_demo.html

# create python environment (only first time)
python3 -m venv visenv
# start environment (having access to environment installed packages)
source visenv/bin/activate
# edit venv with
deactivate

# install any packages needed
pip install matplotlib pandas plotly dash jupyterlab
# save requirements
pip freeze > requirements.txt

# enter local jupyter lab
jupyter lab

# create a single file exe
nuitka myprogram.py

# plotly plot boundaries (y min/max)
https://plotly.com/python/line-charts/

# plotly error bars
https://plotly.com/python/error-bars/