# GCF Tiling Explorer

A Streamlit classroom app for visualizing the Greatest Common Factor (GCF) as the side length of the largest square tile that can fill a rectangle exactly.

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Student interaction

1. A random rectangle is generated.
2. The student chooses one of the square tile sizes.
3. If the tile size is a common factor, the rectangle is tiled and the number of tiles is shown.
4. If it is a common factor but not the GCF, the app tells the student to try a larger square.
5. If it does not fit exactly, the uncovered area is painted red.
6. The rectangle dimensions can also be changed manually.

This is ready to deploy on Streamlit Community Cloud.
