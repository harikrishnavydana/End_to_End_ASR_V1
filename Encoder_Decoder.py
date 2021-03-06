#! /usr/bin/bash

import sys
import torch
import torch.nn as nn
import os
from os.path import join, isdir

import kaldi_io
import torch
from torch import autograd, nn, optim
from torch.autograd import Variable

sys.path.insert(0,'/mnt/matylda3/vydana/HOW2_EXP/Gen_V1/ATTNCODE/Basic_Attention_V1')
from CMVN import CMVN
from utils__ import weights_init,count_parameters,weights_init_tanh

class Encoder_Decoder(nn.Module):
        def __init__(self,args):
                super(Encoder_Decoder, self).__init__()
                #--------------------------------------
                # for adding the Transformwr class
                if 1:   
                        sys.path.insert(0,'/mnt/matylda3/vydana/HOW2_EXP/Gen_V1/ATTNCODE/Basic_Attention_V1')
                        from Res_LSTM_Encoder_arg import Conv_Res_LSTM_Encoder as encoder
                        from Decoder_V1 import decoder


                        self.model_encoder=encoder(args=args)
                        self.model_decoder=decoder(args=args)

                        ##initialize xavier uniform ####default initialize does not work "imay be liked to use some bormalization layers needed"
                        if (str(args.init_full_model)=='xavier_lin_relu'):
                            self.model_encoder.apply(weights_init)
                            self.model_decoder.apply(weights_init)
                        else:
                            pass;

                        print("encoder:=====>",(count_parameters(self.model_encoder))/1000000.0)
                        print("decoder:=====>",(count_parameters(self.model_decoder))/1000000.0)

                #==================================
                else:
                        print("------------------------------------------------->")
        #--------------------------------------
        def forward(self,input,teacher_force_rate,Char_target,Word_target,smp_trans_text):
                 ###encoder of the model
                H = self.model_encoder(input) 
                ###Decoder of the model        
                Decoder_out_dict = self.model_decoder(H, teacher_force_rate, Char_target, Word_target, smp_trans_text)
                return Decoder_out_dict
        #--------------------------------------
        def predict(self,feat_path,args):
                """Input is the path to smp_feat and args file and the it ptodices output_dict"""
                print("went to the decoder loop")
                with torch.no_grad():
                        #### read feature matrices 
                        smp_feat=kaldi_io.read_mat(feat_path)
                        smp_feat=CMVN(smp_feat)
                        input=torch.from_numpy(smp_feat)       
                        input = Variable(input.float(), requires_grad=False).double().float()
                        input=input.unsqueeze(0)


                        print("args.LM_model,args.Am_weight,args.beam,args.gamma,args.len_pen",args.LM_model,args.Am_weight,args.beam,args.gamma,args.len_pen)
                        H=self.model_encoder(input)
                        Output_dict=self.model_decoder.decode_with_beam_LM(H,args.LM_model,args.Am_weight,args.beam,args.gamma,args.len_pen)
                        return Output_dict
