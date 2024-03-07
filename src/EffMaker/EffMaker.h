/*

    Version 1.0 (08.09.2023)

    > First version for CBM in virgo server.

*/

#ifndef YIGE_EFF_MAKER_HEADER
#define YIGE_EFF_MAKER_HEADER

class TH2F;

class EffMaker{
    private:
        static const int nCent = 5;
        TH2F* eff[nCent];
        bool IsCorr;
    
    public:
        EffMaker(){ IsCorr=false; }
        ~EffMaker(){}

        void ReadInEffFile(const char* eff_root_file_path);
        float GetEfficiency(float pt, float y, int centrality);
};

#endif