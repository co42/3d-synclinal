#!/usr/bin/env python3

import numpy as np
import rasterio

PATH_FORMAT = '../height-map-raw/RGEALTI_2-0_1M_ASC_LAMB93-IGN69_D026_2024-01-15/RGEALTI/1_DONNEES_LIVRAISON_2024-06-00238/RGEALTI_MNT_1M_ASC_LAMB93_IGN69_D026_20240629/RGEALTI_FXX_{:04}_{:04}_MNT_LAMB93_IGN69.asc'

def read_transform(path):
    with rasterio.open(path) as src:
        return src.transform

def read_tile(path):
    with rasterio.open(path) as src:
        return src.read(1)

def write_grid(grid, transform, path):
    with rasterio.open(
        path,
        'w',
        driver='GTiff',
        height=grid.shape[0],
        width=grid.shape[1],
        count=1,
        dtype=grid.dtype,
        crs='+proj=latlong',
        transform=transform,
    ) as dst:
        dst.write(grid, 1)

def grid_to_u8(grid):
    min = np.min(grid)
    max = np.max(grid)
    return np.clip((grid - min) / (max - min) * 255, 0, 255).astype(np.uint8)

def grid_to_01(grid):
    min = np.min(grid)
    max = np.max(grid)
    print(min, max)
    grid = np.clip(grid / max, 0, 1)
    min = np.min(grid)
    max = np.max(grid)
    print(min, max)
    return grid

def scale_down(a, factors):
    factors = np.asanyarray(factors)
    sh = np.column_stack([a.shape//factors, factors]).ravel()
    b = a.reshape(sh).mean(tuple(range(1, 2*a.ndim, 2)))
    return b

if __name__ == '__main__':
    xs = list(range(859, 879)) # 20
    ys = list(range(6392, 6404)) # 12
    transform = read_transform(PATH_FORMAT.format(xs[0], ys[0]))
    grid = np.concatenate(list(reversed([
        np.concatenate([
            read_tile(PATH_FORMAT.format(x, y))
            for x in xs
        ], axis=1)
        for y in ys
    ])), axis=0)
    scale_down(grid, (4, 4))
    write_grid(grid, transform, '../height-map.tif')
