#include "sndfile.h"
#include <fftw3.h>

class Processor{
    protected:
        SF_INFO m_fileInfo;
        SNDFILE *m_file;
        mutable float *m_buffer;
        const char *m_path;
        size_t m_frameCount;
        size_t m_channelCount;
        size_t m_sampleRate;
        mutable size_t m_bufsize;
        const int FFT_SIZE = 2048;
        fftw_plan trans;
        fftw_complex *fft_in,*fft_out;
        void handler(int sig);
    public:
        virtual ~Processor();
        Processor(const char * path);
        void to_mono(fftw_complex* fft_data, sf_count_t count);
        sf_count_t read_frames(size_t start);
        void process();
        
};
