       //
       // Calcul dimension zone receveuse
       //
       PyObject* sol;  PyObject* t;

       sol = K_PYTREE::getNodeFromName1(zoneR , "FlowSolution#Centers");
       if(sol != NULL)
       {  
         ipt_roR[nd]   = NULL;
         t                           = K_PYTREE::getNodeFromName1(sol, varname );
         if(t != NULL) ipt_roR[nd]   = K_PYTREE::getValueAF(t, hook);

	 if(iscalcMacro_LBM==1){
	   ipt_macros_localR[nd]  = NULL;
	   t                      = K_PYTREE::getNodeFromName1(sol,"Density" );
	   if(t != NULL)
	     ipt_macros_localR[nd]= K_PYTREE::getValueAF(t, hook);
	 }
	 
	 if(isIBM==1 || lbm_octree ==1){
	   ipt_Qneq_localR[nd]  = NULL;
	   t                    = K_PYTREE::getNodeFromName1(sol,"Qneq_1" );
	   if(t != NULL)
	     ipt_Qneq_localR[nd]= K_PYTREE::getValueAF(t, hook);

	   ipt_cellNIBC_R[nd]  = NULL;
	   t                    = K_PYTREE::getNodeFromName1(sol,"cellN_IBC_LBM_1" );
	   if(t != NULL)
	     ipt_cellNIBC_R[nd]= K_PYTREE::getValueAF(t, hook);
	 }
	 
	 if(isneedQstar==1){
	   ipt_Qstar_localR[nd]  = NULL;
	   t                     = K_PYTREE::getNodeFromName1(sol,"Qstar_1" );
	   if(t != NULL)
	     ipt_Qstar_localR[nd]= K_PYTREE::getValueAF(t, hook);
	 }
	 
       }

       sol = K_PYTREE::getNodeFromName1(zoneR , "FlowSolution");
       if(sol != NULL)
       {  
         ipt_roR_vert[nd] = NULL;
         t                              = K_PYTREE::getNodeFromName1(sol, varname );
         if(t != NULL) ipt_roR_vert[nd] = K_PYTREE::getValueAF(t, hook);
       }

        PyObject* own      = K_PYTREE::getNodeFromName1(zoneR , ".Solver#ownData");
                t          = K_PYTREE::getNodeFromName1(own, "Parameter_int");
        ipt_param_intR[nd] = K_PYTREE::getValueAI(t, hook);

                t          = K_PYTREE::getNodeFromName1(own, "Parameter_real");
        ipt_param_realR[nd]= K_PYTREE::getValueAF(t, hook);



/*        char* type; E_Int s, s0, s1;  E_Int* d;
        // get type
        t    =  K_PYTREE::getNodeFromName1(zoneR, "ZoneType");
        type =  K_PYTREE::getValueS(t, s, hook);
        // get dims zone receveuse
        d    =  K_PYTREE::getValueAI(zoneR, s0, s1, hook);

        if (K_STRING::cmp(type, s, "Structured") == 0)
         {
          if      (s0 == 1){ ipt_ndimdxR[nd + nidomR]= d[0]          ; ipt_ndimdxR[nd]= d[3];           }
          else if (s0 == 2){ ipt_ndimdxR[nd + nidomR]= d[0]*d[1]     ; ipt_ndimdxR[nd]= d[3]*d[4];      }
          else if (s0 == 3){ ipt_ndimdxR[nd + nidomR]= d[0]*d[1]*d[2]; ipt_ndimdxR[nd]= d[3]*d[4]*d[5]; }
         }

        else // non structure
         {
              ipt_ndimdxR[nd        ]= d[0]* d[1]; // npoint, nelements
              ipt_ndimdxR[nd+ nidomR]= d[0]* d[1]; // pourquoi pas de dependance a la localisation en non structure??
         }
*/
