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
};

#endif /* PROCESSINGTOOLS_H_ */
