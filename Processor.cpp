#include <iostream>
#include <fstream> 

#include <stdio.h>
#include <stdlib.h>     /* exit, EXIT_FAILURE */
#include <signal.h>
#include <execinfo.h>
#include <unistd.h>

#include "Processor.h"
#include "ProcessingTools.h"


Processor::Processor(const char* path, const bool debug) :
m_file(0),
m_buffer(0),
m_bufsize(0)
{
    std::cout << "Reading file at " << path << std::endl;
    m_path = path;
    DEBUG_ENABLED = debug;
    m_frameCount = 0;
    m_channelCount = 0;
    m_sampleRate = 0;

    m_fileInfo.format = 0;
    m_fileInfo.frames = 0;
        
    fft_in = fftw_alloc_complex(FFT_SIZE);
    fft_out = fftw_alloc_complex(FFT_SIZE);
    trans = fftw_plan_dft_1d(FFT_SIZE,fft_in,fft_out,FFTW_FORWARD,FFTW_MEASURE);
    
    m_file = sf_open(path, SFM_READ, &m_fileInfo);
    if(!m_file){
        std::cerr << "error reading file " << sf_strerror(m_file) << std::endl;
        return;
    }
    if (m_fileInfo.channels > 0) {
        m_frameCount = m_fileInfo.frames;
        m_channelCount = m_fileInfo.channels;
        m_sampleRate = m_fileInfo.samplerate;
    }
    m_bufsize = FFT_SIZE * m_fileInfo.channels;
    m_buffer = new float[m_bufsize];
    magnitudes = new float[FFT_SIZE];
}

Processor::~Processor()
{
}

SDL_Renderer* Processor::yield_renderer(){
    int height = 500;
    if(SDL_Init(SDL_INIT_VIDEO | SDL_INIT_TIMER) < 0)
    {
        /* Handle problem */
        fprintf(stderr, "%s\n", SDL_GetError());
        exit(EXIT_FAILURE);
    }
	SDL_Window* window = SDL_CreateWindow("Plot",
                                SDL_WINDOWPOS_UNDEFINED,
                                SDL_WINDOWPOS_UNDEFINED,
                                FFT_SIZE,
                                height,
                                SDL_WINDOW_RESIZABLE);
	SDL_Renderer* renderer = SDL_CreateRenderer(window, -1, 0);
    if(renderer == NULL)
    {
        /* Handle problem */
        fprintf(stderr, "%s\n", SDL_GetError());
        SDL_Quit();
        exit(EXIT_FAILURE);
    }
    return renderer;
}

sf_count_t Processor::read_frames(size_t start){
    size_t count = m_bufsize;
    sf_count_t readCount = 0;
    if (!m_file || !m_channelCount) {
        std::cerr << "no file or no channel" << std::endl;
        return 0;
    }
    if ((long)start >= m_fileInfo.frames) {
        std::cerr << "end of file" << std::endl;
	    return 0;
    }
    if (long(start + m_bufsize) > m_fileInfo.frames) {
	    count = m_fileInfo.frames - start;
    }
    if (sf_seek(m_file, start, SEEK_SET) < 0) {
        std::cerr << "sf_seek failed" << std::endl;
	    exit(EXIT_FAILURE);
	}
    if ((readCount = sf_readf_float(m_file, m_buffer, count)) < 0) {
        std::cerr << "sf_readf_float failed" << std::endl;
	    exit(EXIT_FAILURE);
	}
    //std::cout << readCount << std::endl;
    return readCount;
}

void handler(int sig) {
  void *array[10];
  size_t size;

  // get void*'s for all entries on the stack
  size = backtrace(array, 10);

  // print out all the frames to stderr
  fprintf(stderr, "Error: signal %d:\n", sig);
  backtrace_symbols_fd(array, size, STDERR_FILENO);
  exit(1);
}

// Takes the content of m_buffer, converts it to mono and writes it in an array 
// to be used as FFT input. If less frames where read than required because the 
// end of the file was reached (count < m_bufsize), fill with Os.
void Processor::to_mono(fftw_complex* fft_data, sf_count_t count){
    int i = 0;
    int j = 0;
    //~ std::cout << "buffer " << m_bufsize << " " << std::endl;
    if( DEBUG_ENABLED ){
        std::cout << "buffer " << m_bufsize << " " << std::endl;
    }
    for(i=0; i < m_bufsize/m_channelCount; i++){
        float audio_data = 0;
        for(j = 0; j < m_channelCount; j++){
            if(i*m_channelCount+j < count)
                audio_data += m_buffer[i*m_channelCount+j];
        }
        if( DEBUG_ENABLED ){
            std::cout << audio_data << " ";
        }
        audio_data /= m_channelCount;
        fft_in[i][0] = audio_data;
        fft_in[i][1] = 0.;
    }
    if( DEBUG_ENABLED ){
        std::cout << std::endl;
        std::cout << "spectrum" << std::endl;
        for(int k = 0; k < FFT_SIZE; k++){
            std::cout << fft_in[k][0] << " " ;
        }
        std::cout << std::endl;
    }
}

void Processor::process(){
    std::cout << "Processing file." << std::endl;
    SDL_Renderer* renderer = yield_renderer();
    size_t frame_idx = 0;
    sf_count_t readCount = 0;

    int i = 0;
    
    float centroid = 0;
    float flow = 0;

    float to_wait = FFT_SIZE / float(m_sampleRate);
    bool must_break = false;
    float* previous_magnitudes = new float[FFT_SIZE];
    for (int j = 0; j < FFT_SIZE; ++j) {
        previous_magnitudes[j] = 0;
    }

    while((readCount = read_frames(frame_idx)) > 0){
        to_mono(fft_in, readCount);
        frame_idx+=readCount;
        fftw_execute(trans);
        ProcessingTools::get_magnitude(magnitudes, fft_out, FFT_SIZE);
        ProcessingTools::plotData(renderer, magnitudes, FFT_SIZE/2);
        std::cout << "plotted" << std::endl;
        SDL_Event event;

        /* Poll for events */
        while( SDL_PollEvent( &event ) ){
            std::cout << event.type << std::endl;  
            switch( event.type ){
                case SDL_QUIT:
                    must_break = true;
                    break;
    
                default:
                    break;
            }
        }
        if(must_break){
            break;
        }
        SDL_Delay(500);
        if( i < NUMBER_OF_WINDOWS ){
            fftw_execute(trans);
            for(int j=0; j < m_bufsize/m_channelCount; j++){
                if( DEBUG_ENABLED ){
                    std::cout << fft_in[j][0];
                }
            }
            float* magnitudes = new float[FFT_SIZE];
            float* lolz = ProcessingTools::get_magnitude(magnitudes, fft_out, FFT_SIZE);
            float result_centroids = ProcessingTools::compute_centroid(magnitudes, FFT_SIZE);
            centroid += result_centroids;

            float result_flow = ProcessingTools::compute_flow(magnitudes, previous_magnitudes, FFT_SIZE);
            flow += result_flow;
            if(DEBUG_ENABLED){
                std::cout << "Centroid: ";
                std::cout << result_centroids << std::endl;

                std::cout << "Flow: ";
                std::cout << result_flow << std::endl;
            }
            for( int j = 0; j < FFT_SIZE; ++j){
                previous_magnitudes[j] = magnitudes[j];
            }
            i++;
        }else{
            break;
        }
    }
 

    std::cout << "Centroid: ";
    std::cout << (centroid/NUMBER_OF_WINDOWS) << std::endl;

    std::cout << "Flow: ";
    std::cout << (flow/NUMBER_OF_WINDOWS) << std::endl;

    std::cout << "Processing file done." << std::endl;
    SDL_DestroyRenderer(renderer);
    SDL_Quit();
}

fftw_complex* Processor::get_fft_in(){
    return fft_in;
}

fftw_complex* Processor::get_fft_out(){
    return fft_out;
}

void save_to_file(float* data)
{
    std::cout << "Trying to save data into output file." << std::endl;
    std::ofstream fout("output.txt");
    if(fout.is_open())
    {
        for(int i = 0; i < 2048; i++) {
            fout << data[i];
            //fout << "\n";
        }
        std::cout << "Array data saved into output file." << std::endl;
    }
    else {
        std::cout << "File could not be opened." << std::endl;
    }
    fout.close();
}

int main(int argc, char** argv){
    signal(SIGSEGV, handler);
    if(argc >=1){
        Processor p(argv[1], false);
        p.process();
    }
    return 0;
}
