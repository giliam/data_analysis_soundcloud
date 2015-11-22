#include <iostream>
#include <stdio.h>
#include <stdlib.h>     /* exit, EXIT_FAILURE */
#include "Processor.h"
#include <execinfo.h>
#include <execinfo.h>
#include <signal.h>
#include <unistd.h>

Processor::Processor(const char* path) :
m_file(0),
m_buffer(0),
m_bufsize(0)
{
    std::cout << "Reading file at " << path << std::endl;
    m_path = path;
    m_frameCount = 0;
    m_channelCount = 0;
    m_sampleRate = 0;

    m_fileInfo.format = 0;
    m_fileInfo.frames = 0;
        
    fft_in = fftw_alloc_complex(FFT_SIZE);
    fft_out = fftw_alloc_complex(FFT_SIZE);
    trans=fftw_plan_dft_1d(FFT_SIZE,fft_in,fft_out,FFTW_FORWARD,FFTW_MEASURE);
    
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
}

Processor::~Processor()
{
    delete[] m_buffer;
}

sf_count_t Processor::read_frames(size_t start){
    size_t count = FFT_SIZE;
    sf_count_t readCount = 0;
    if (!m_file || !m_channelCount) {
        return 0;
    }
    if ((long)start >= m_fileInfo.frames) {
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
    for(i=0; i < m_bufsize/m_channelCount; i++){
        float audio_data = 0;
        for(j = 0; j < m_channelCount; j++){
            if(i*m_channelCount+j < count)
                audio_data += m_buffer[i*m_channelCount+j];
        }
        audio_data /= m_channelCount;
        fft_in[i][0] = audio_data;
        fft_in[i][1] = 0.;
    }
}

void Processor::process(){
    size_t frame_idx = 0;
    sf_count_t readCount = 0;
    while((readCount = read_frames(frame_idx)) >= 0){
        to_mono(fft_in, readCount);
    }
}


int main(int argc, char** argv){
    signal(SIGSEGV, handler);
    if(argc >=1){
        Processor p(argv[1]);
    }
    return 0;
}
