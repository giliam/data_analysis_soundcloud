#include "sndfile.h"
#include <fftw3.h>
#include <SDL2/SDL.h>

class Processor{
    protected:
        bool DEBUG_ENABLED = false;
        int NUMBER_OF_WINDOWS = 100;
        SF_INFO m_fileInfo;
        SNDFILE *m_file;
        mutable float *m_buffer;
        const char *m_path;
        size_t m_frameCount;
        size_t m_channelCount;
        size_t m_sampleRate;
        mutable size_t m_bufsize;
        fftw_plan trans;
        fftw_complex *fft_in,*fft_out;
        void handler(int sig);
    public:
        const int FFT_SIZE = 2048;
        virtual ~Processor();
        Processor(const char * path, const bool debug);
        void to_mono(fftw_complex* fft_data, sf_count_t count);
        sf_count_t read_frames(size_t start);
        void process();
        fftw_complex* get_fft_in();
        fftw_complex* get_fft_out();
        SDL_Renderer* yield_renderer();

};
