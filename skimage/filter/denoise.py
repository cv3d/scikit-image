import numpy as np
from skimage import img_as_float
import _denoise


def _tv_denoise_3d(im, weight=100, eps=2.e-4, n_iter_max=200):
    """Perform total-variation denoising on 3-D arrays.

    Parameters
    ----------
    im: ndarray
        3-D input data to be denoised.
    weight: float, optional
        Denoising weight. The greater ``weight``, the more denoising (at
        the expense of fidelity to ``input``).
    eps: float, optional
        Relative difference of the value of the cost function that determines
        the stop criterion. The algorithm stops when:

            (E_(n-1) - E_n) < eps * E_0

    n_iter_max: int, optional
        Maximal number of iterations used for the optimization.

    Returns
    -------
    out: ndarray
        Denoised array of floats.

    Notes
    -----
    Rudin, Osher and Fatemi algorithm.

    Examples
    ---------
    First build synthetic noisy data
    >>> x, y, z = np.ogrid[0:40, 0:40, 0:40]
    >>> mask = (x -22)**2 + (y - 20)**2 + (z - 17)**2 < 8**2
    >>> mask = mask.astype(np.float)
    >>> mask += 0.2*np.random.randn(*mask.shape)
    >>> res = tv_denoise_3d(mask, weight=100)
    """
    px = np.zeros_like(im)
    py = np.zeros_like(im)
    pz = np.zeros_like(im)
    gx = np.zeros_like(im)
    gy = np.zeros_like(im)
    gz = np.zeros_like(im)
    d = np.zeros_like(im)
    i = 0
    while i < n_iter_max:
        d = - px - py - pz
        d[1:] += px[:-1]
        d[:, 1:] += py[:, :-1]
        d[:, :, 1:] += pz[:, :, :-1]

        out = im + d
        E = (d**2).sum()

        gx[:-1] = np.diff(out, axis=0)
        gy[:, :-1] = np.diff(out, axis=1)
        gz[:, :, :-1] = np.diff(out, axis=2)
        norm = np.sqrt(gx**2 + gy**2 + gz**2)
        E += weight * norm.sum()
        norm *= 0.5 / weight
        norm += 1.
        px -= 1. / 6. * gx
        px /= norm
        py -= 1. / 6. * gy
        py /= norm
        pz -= 1 / 6. * gz
        pz /= norm
        E /= float(im.size)
        if i == 0:
            E_init = E
            E_previous = E
        else:
            if np.abs(E_previous - E) < eps * E_init:
                break
            else:
                E_previous = E
        i += 1
    return out


def _tv_denoise_2d(im, weight=50, eps=2.e-4, n_iter_max=200):
    """Perform total-variation denoising.

    Parameters
    ----------
    im: ndarray
        Input data to be denoised.
    weight: float, optional
        Denoising weight. The greater ``weight``, the more denoising (at
        the expense of fidelity to ``input``)
    eps: float, optional
        Relative difference of the value of the cost function that determines
        the stop criterion. The algorithm stops when:

            (E_(n-1) - E_n) < eps * E_0

    n_iter_max: int, optional
        Maximal number of iterations used for the optimization.

    Returns
    -------
    out: ndarray
        Denoised array of floats.

    Notes
    -----
    The principle of total variation denoising is explained in
    http://en.wikipedia.org/wiki/Total_variation_denoising.

    This code is an implementation of the algorithm of Rudin, Fatemi and Osher
    that was proposed by Chambolle in [1]_.

    References
    ----------
    .. [1] A. Chambolle, An algorithm for total variation minimization and
           applications, Journal of Mathematical Imaging and Vision,
           Springer, 2004, 20, 89-97.

    Examples
    ---------
    >>> import scipy
    >>> lena = scipy.lena()
    >>> import scipy
    >>> lena = scipy.lena().astype(np.float)
    >>> lena += 0.5 * lena.std()*np.random.randn(*lena.shape)
    >>> denoised_lena = tv_denoise(lena, weight=60.0)
    """
    px = np.zeros_like(im)
    py = np.zeros_like(im)
    gx = np.zeros_like(im)
    gy = np.zeros_like(im)
    d = np.zeros_like(im)
    i = 0
    while i < n_iter_max:
        d = -px - py
        d[1:] += px[:-1]
        d[:, 1:] += py[:, :-1]

        out = im + d
        E = (d**2).sum()
        gx[:-1] = np.diff(out, axis=0)
        gy[:, :-1] = np.diff(out, axis=1)
        norm = np.sqrt(gx**2 + gy**2)
        E += weight * norm.sum()
        norm *= 0.5 / weight
        norm += 1
        px -= 0.25 * gx
        px /= norm
        py -= 0.25 * gy
        py /= norm
        E /= float(im.size)
        if i == 0:
            E_init = E
            E_previous = E
        else:
            if np.abs(E_previous - E) < eps * E_init:
                break
            else:
                E_previous = E
        i += 1
    return out


def tv_denoise(im, weight=50, eps=2.e-4, n_iter_max=200):
    """Perform total-variation denoising on 2-d and 3-d images.

    Parameters
    ----------
    im: ndarray (2d or 3d) of ints, uints or floats
        Input data to be denoised. `im` can be of any numeric type,
        but it is cast into an ndarray of floats for the computation
        of the denoised image.
    weight: float, optional
        Denoising weight. The greater ``weight``, the more denoising (at
        the expense of fidelity to ``input``).
    eps: float, optional
        Relative difference of the value of the cost function that
        determines the stop criterion. The algorithm stops when:

            (E_(n-1) - E_n) < eps * E_0

    n_iter_max: int, optional
        Maximal number of iterations used for the optimization.

    Returns
    -------
    out: ndarray
        Denoised array of floats.

    Notes
    -----
    The principle of total variation denoising is explained in
    http://en.wikipedia.org/wiki/Total_variation_denoising

    The principle of total variation denoising is to minimize the
    total variation of the image, which can be roughly described as
    the integral of the norm of the image gradient. Total variation
    denoising tends to produce "cartoon-like" images, that is,
    piecewise-constant images.

    This code is an implementation of the algorithm of Rudin, Fatemi and Osher
    that was proposed by Chambolle in [1]_.

    References
    ----------
    .. [1] A. Chambolle, An algorithm for total variation minimization and
           applications, Journal of Mathematical Imaging and Vision,
           Springer, 2004, 20, 89-97.

    Examples
    ---------
    >>> import scipy
    >>> # 2D example using lena
    >>> lena = scipy.lena()
    >>> import scipy
    >>> lena = scipy.lena().astype(np.float)
    >>> lena += 0.5 * lena.std()*np.random.randn(*lena.shape)
    >>> denoised_lena = tv_denoise(lena, weight=60)
    >>> # 3D example on synthetic data
    >>> x, y, z = np.ogrid[0:40, 0:40, 0:40]
    >>> mask = (x -22)**2 + (y - 20)**2 + (z - 17)**2 < 8**2
    >>> mask = mask.astype(np.float)
    >>> mask += 0.2*np.random.randn(*mask.shape)
    >>> res = tv_denoise_3d(mask, weight=100)
    """
    im_type = im.dtype
    if not im_type.kind == 'f':
        im = img_as_float(im)

    if im.ndim == 2:
        out = _tv_denoise_2d(im, weight, eps, n_iter_max)
    elif im.ndim == 3:
        out = _tv_denoise_3d(im, weight, eps, n_iter_max)
    else:
        raise ValueError('only 2-d and 3-d images may be denoised with this '
                         'function')
    return out


def denoise_bilateral(image, win_size=5, sigma_color=1, sigma_range=1, bins=1e4,
                      mode='constant', cval=0):
    """Denoise image using bilateral filter.

    This is an edge-preserving and noise reducing denoising filter. It averages
    pixels based on their spatial closeness and radiometric similarity.

    Spatial closeness is measured by the gaussian function of the euclidian
    distance between two pixels and a certain standard deviation
    (`sigma_range`).

    Radiometric similarity is measured by the gaussian function of the euclidian
    distance between two color values and a certain standard deviation
    (`sigma_color`).

    Parameters
    ----------
    image : ndarray
        Input image.
    win_size : int
        Window size for filtering.
    sigma_color : float
        Standard deviation for color distance. A larger value results in
        averaging of pixels with larger color differences.
    sigma_range : float
        Standard deviation for range distance. A larger value results in
        averaging of pixels with larger spatial differences.
    bins : int
        Number of discrete values for gaussian weights of color filtering.
        A larger value results in improved accuracy.
    mode : string
        How to handle values outside the image borders. See
        `scipy.ndimage.map_coordinates` for detail.
    cval : string
        Used in conjunction with mode 'constant', the value outside
        the image boundaries.

    Returns
    -------
    denoised : ndarray
        Denoised image.

    References
    ----------
    .. [1] http://users.soe.ucsc.edu/~manduchi/Papers/ICCV98.pdf

    """

    # not using img_as_float to preserve original range of values, which is
    # necessary so sigma_color is applied as user desires
    image = np.array(image, dtype=np.double)

    if mode not in ('constant', 'wrap', 'reflect', 'nearest'):
        raise ValueError("Invalid mode specified.  Please use "
                         "`constant`, `nearest`, `wrap` or `reflect`.")
    mode = ord(mode[0].upper())

    if image.ndim == 2 or (image.ndim == 3 and image.shape[2] == 1):
        if image.ndim == 3 and image.shape[2] == 1:
            image = np.squeeze(image)
        func = _denoise._denoise_bilateral2d
    else:
        func = _denoise._denoise_bilateral3d
    image = np.ascontiguousarray(image)
    return func(image, win_size, sigma_color, sigma_range, bins, mode, cval)
