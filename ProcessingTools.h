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
#include <Eigen/SparseCore>
#include <Eigen/Core>
#include "type.h"


class ProcessingTools {
public:
	ProcessingTools();
	static int nextpow2(int x);
	static double* hamming(int N);
	static double* blackmann(int N);
	static double max(double * array, int N);
	static double max(std::vector<double>* array, int N);
	static double max(Eigen::Matrix<Complex,Eigen::Dynamic,1>* array, int N);
	//static double mean(Eigen::Matrix<Complex,Eigen::Dynamic,1>* array, int s, int e);
	template<typename T>
	static double mean(T* array, int s, int e);
	template<typename T>
	static void plotData(T* data, int l);
	//static void plotData(Eigen::Matrix<Complex,Eigen::Dynamic,1>* data, int l);
	virtual ~ProcessingTools();
};

#endif /* PROCESSINGTOOLS_H_ */
