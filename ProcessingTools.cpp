/*
 * ProcessingTools.cpp
 *
 *  Created on: 4 sept. 2014
 *      Author: anis
 */

#include "ProcessingTools.h"
#include <fstream> 

#include <cmath>
#include <iostream>
#include <cstdio>

#include <stdlib.h>     /* exit, EXIT_FAILURE */


ProcessingTools::ProcessingTools() {
	std::cout << "COUCOU" << std::endl;
}

int ProcessingTools::nextpow2(int x){
	int k = 0;
	while(x >= 1){
		x = x/2;
		k++;
	}
	return k;
}

double* ProcessingTools::hamming(int N){
	double* hamming = new double[N];
	for(int k = 0; k < N; k++){
		hamming[k] = 0.54 - 0.46*cos((2*M_PI*k)/N) ;
	}
	return hamming;
}

double* ProcessingTools::blackmann(int N){
	double* blackmann = new double[N];
	for(int k = 0; k < N; k++){
		blackmann[k] = (0.42 - 0.5*cos((2*M_PI*k)/N) + 0.08*cos((4*M_PI*k)/N));
	}
	return blackmann;
}


double ProcessingTools::max(double * array, int N){
	double tmp = 0;
	for(int k=0; k<N; k++){
		if(array[k] > tmp){
			tmp = array[k];
		}
	}

	return tmp;
}


double ProcessingTools::max(std::vector<double>* array, int N){
	int i;
	double tmp = 0;
	for(int k=0; k <N; k++){
		if((*array)[k] > tmp){
			tmp = (*array)[k];
			i = k;
		}
	}
	std::cout << "max index for " << i << std::endl;
	return tmp;
}

template<typename T>
double ProcessingTools::mean(T* array, int s, int e){
	double sum = 0;
	for(int i=s; i < e; i++)
		sum+=std::abs((*array)[i]);
	return sum/(e-s);
}

float* ProcessingTools::get_magnitude(float* magnitudes, fftw_complex* data, const int FFT_SIZE){
	for (int i = 0; i < FFT_SIZE; ++i)
	{
		magnitudes[i] = std::sqrt(data[i][0]*data[i][0]+data[i][1]*data[i][1]);
	}
    return magnitudes;
}


float ProcessingTools::compute_centroid(float* fft_out, const int FFT_SIZE){
    float up = 0, down = 0;
    for (int i = 0; i < FFT_SIZE; ++i)
    {
        up += i*fft_out[i];
        down += fft_out[i];
    }
    if(down == 0){
        std::cerr << "divide by zero" << std::endl;
        //exit(EXIT_FAILURE);
        return 0;
    }
    return up/down;
}

template<typename T>
void ProcessingTools::plotData(T* data, int l){
	int height=500;
	int colWidth = 1;
	int offsetX = 10;
	int width=std::min(l, 1200);
	int step = std::ceil(l/double(width));
	std::cout << "step=" << step << std::endl;
	if(SDL_Init(SDL_INIT_VIDEO) < 0)
    {
        /* Handle problem */
        fprintf(stderr, "%s\n", SDL_GetError());
    }
	SDL_Window* window = SDL_CreateWindow("Plot",
                                      SDL_WINDOWPOS_UNDEFINED,
                                      SDL_WINDOWPOS_UNDEFINED,
                                      width+2*offsetX,
                                      height,
                                      SDL_WINDOW_RESIZABLE);
	SDL_Surface *ecran = NULL;
	SDL_Event event;
	ecran = SDL_GetWindowSurface(window);
	SDL_Renderer* renderer = SDL_CreateRenderer(window, -1, 0);
    if(renderer == NULL)
    {
        /* Handle problem */
        fprintf(stderr, "%s\n", SDL_GetError());
        SDL_Quit();
    }
    SDL_Rect r;
    r.y = height/2;
    r.w = colWidth;
    SDL_SetRenderDrawColor(renderer, 255, 255, 255, 255 );


	// Clear window
    SDL_RenderClear( renderer );
    SDL_SetRenderDrawColor(renderer, 0, 0, 0, 255 );

	double m = ProcessingTools::max(data, l);
	std::cout << "m=" << m << std::endl;
	for(int k = 0; k < l-step; k+=step){
		r.x = k*colWidth/step+offsetX;
    	r.h = -(height/2)*(ProcessingTools::mean(data, k, k+step)/m);
	    SDL_RenderFillRect(renderer, &r );
	    r.h = - r.h;
	    SDL_RenderFillRect(renderer, &r );
	}
	SDL_RenderPresent(renderer);
	bool goOn = true;
	while (goOn){
		SDL_PollEvent(&event);
		if(event.type == SDL_QUIT){
			goOn = false;
		}
	}
    //SDL_Quit();

}


void ProcessingTools::plotData(SDL_Renderer* renderer, float* magnitudes, int l){
    // Clear window
    SDL_SetRenderDrawColor(renderer, 255, 255, 255, 255 );
    SDL_RenderClear( renderer );
    SDL_SetRenderDrawColor(renderer, 0, 0, 0, 255 );
    SDL_Rect r;
    r.y = 500;
    r.w = 1;
    std::cout << "plot" << std::endl;
    for(int k = 1; k < l; k++){
		r.x = k;
    	r.h = magnitudes[k]*100;
        std::cout << "height is " << r.h << " " << k << " ";
	    SDL_RenderFillRect(renderer, &r);
	}
    std::cout << "finished" << std::endl;
    SDL_RenderPresent(renderer);
    std::cout << "rendered" << std::endl;
}


ProcessingTools::~ProcessingTools() {
	// TODO Auto-generated destructor stub
}

