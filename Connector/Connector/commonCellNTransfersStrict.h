
type = types[noind];
SIZECF(type, meshtype, sizecoefs);

nocf = 0;
E_Float val = 1.;
// - pas de cellule masquee, ni interpolee dans la molecule d interpolation, sauf si son cf associe est nul.
// - somme des cf = 1.
// -----------------
// cellN*(2-cellN) renvoie 0 si cellN = 0 ou 2 (pt masque ou interpolee) et 1 si cellN =1 (pt calcule)
switch (type)
{
  case 0:  //  nuage de pts quelconque
    ncfLoc = donorPts[noi];// nb de pts pour la formule
    for (E_Int kk = 1; kk <= ncfLoc; kk++)
    {
      indD0 = donorPts[noi+kk];
      val *= cellND[indD0]*(2.-cellND[indD0]);   
    }
    if ( val > 0.5 ) cellNR[indR] = 1.;//egal a 1 
    else cellNR[indR] = 0.;
    
    sizecoefs = ncfLoc;
    noi += ncfLoc+1;
    break;
    
  case 1:
    indD0 = donorPts[noi];
    val = cellND[indD0]*(2.-cellND[indD0]);     
    if ( val > 0.5 ) cellNR[indR] = 1.;//egal a 1 
    else cellNR[indR] = 0.;
    sizecoefs = 1;
    noi+=1;
    break;
    
  case 2: // Structure Lineaire O2 par tetra
    indD0 = donorPts[noind];
    k = indD0/imdjmd;
    j = (indD0-k*imdjmd)/imd;
    i = (indD0-j*imd-k*imdjmd);
    for (E_Int kk=0; kk<2; kk++)
      for (E_Int jj=0; jj<2; jj++)
        for (E_Int ii=0; ii<2; ii++)
        {
          indD = (i+ii)+(j+jj)*imd+(k+kk)*imdjmd;
          val *= cellND[indD]*(2.-cellND[indD]);   
          nocf++;
        }
    
    if ( val > 0.5 ) cellNR[indR] = 1.;//egal a 1 
    else cellNR[indR] = 0.;
    noi += 1;
    break;
    
  case 22:// O2CF 2D
    indD0 = donorPts[noind];
    j = indD0/imd;
    i = indD0-j*imd;
    for (E_Int jj=0; jj<2; jj++)
      for (E_Int ii=0; ii<2; ii++)
      {
        indD = (i+ii)+(j+jj)*imd;
        val *= cellND[indD]*(2.-cellND[indD]);   
        nocf++;
      }      
    if ( val > 0.5 ) cellNR[indR] = 1.;//egal a 1 
    else cellNR[indR] = 0.;
    noi += 1;
    break;
    
  case 3: // Lagrange O3
    indD0 = donorPts[noind];
    k = indD0/imdjmd;
    j = (indD0-k*imdjmd)/imd;
    i = (indD0-j*imd-k*imdjmd);
    
    for (E_Int kk=0; kk<3; kk++)
      for (E_Int jj=0; jj<3; jj++)
        for (E_Int ii=0; ii<3; ii++)
        {
          indD = (i+ii)+(j+jj)*imd+(k+kk)*imdjmd;
          val *= cellND[indD]*(2.-cellND[indD]);             
        }
    if ( val > 0.5 ) cellNR[indR] = 1.;//egal a 1 
    else cellNR[indR] = 0.;
    noi += 1;
    break;
    
  case 4: // Tetra O2
    indD0 = donorPts[noind];
    // indD0 est le no de l elt, et les coefs sont aux noeuds
    for (E_Int nov = 1; nov <= 4; nov++)
    {
      E_Int indv = ptrcnd[indD0*cnNfldD+nov-1]-1;
      val *= cellND[indv]*(2.-cellND[indv]);        
    }  
    if ( val > 0.5 ) cellNR[indR] = 1.;//egal a 1 
    else cellNR[indR] = 0.;
    noi += 1;      
    break;
    
  case 5: // Lagrange O5
    indD0 = donorPts[noind];
    k = indD0/imdjmd;
    j = (indD0-k*imdjmd)/imd;
    i = (indD0-j*imd-k*imdjmd);
    for (E_Int kk=0; kk<5; kk++)
      for (E_Int jj=0; jj<5; jj++)
        for (E_Int ii=0; ii<5; ii++)
        {
          indD = (i+ii)+(j+jj)*imd+(k+kk)*imdjmd;
          val *= cellND[indD]*(2.-cellND[indD]);         
        }
    if ( val > 0.5 ) cellNR[indR] = 1.;//egal a 1 
    else cellNR[indR] = 0.;
    noi += 1;
    break;
    
  default:;
}
