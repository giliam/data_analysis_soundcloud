/*
 * ProcessingTools.h
 *
 *  Created on: 4 sept. 2014
 *      Author: anis
 */

#ifndef PROCESSINGTOOLS_H_
#define PROCESSINGTOOLS_H_
#include <vector>
#include <complex>
#include <stdlib.h>     /* exit, EXIT_FAILURE */
#include <fftw3.h>
#include <SDL2/SDL.h>
#include "sndfile.h"


class ProcessingTools {
public:
	ProcessingTools();
	static int nextpow2(int x);
	static double* hamming(int N);
	static double* blackmann(int N);
	static double max(double * array, int N);
	static double max(std::vector<double>* array, int N);
	template<typename T>
	static double mean(T* array, int s, int e);
	template<typename T>
	static void plotData(T* data, int l);
	//static void plotData(Eigen::Matrix<Complex,Eigen::Dynamic,1>* data, int l);
	virtual ~ProcessingTools();
	static float* get_magnitude(float* magnitudes, fftw_complex* data, const int FFT_SIZE);
	static float compute_centroid(float* fft_out, const int FFT_SIZE);
    static void plotData(SDL_Renderer* renderer, float* data, int length);
    static float compute_flow(float* fft_window, float* previous_fft_window, const int FFT_SIZE);
    static void plotData(SDL_Renderer* renderer, fftw_complex* data, int length);
};

#endif /* PROCESSINGTOOLS_H_ */
