
dtmc

const N;

module TaxiConfMat

  cte : [-4..4] init 0;
  he : [-2..2] init 0;
  cte_est : [-2..2] init 0;
  he_est : [-1..1] init 0;
  a : [-1..1] init 0;
  pc : [0..7] init 0; // program counter
  k : [0..N] init 1; // loop counter


  // Perceiver (CTE)
  [] cte=-2  & pc=0 -> 0.1708542713567839 : (cte_est'=-2) & (pc'=1) + 0.24623115577889448 : (cte_est'=-1) & (pc'=1) + 0.19095477386934673 : (cte_est'=0) & (pc'=1) + 0.1457286432160804 : (cte_est'=1) & (pc'=1) + 0.24623115577889448 : (cte_est'=2) & (pc'=1) ;
  [] cte=-1  & pc=0 -> 0.22105263157894736 : (cte_est'=-2) & (pc'=1) + 0.20526315789473684 : (cte_est'=-1) & (pc'=1) + 0.2 : (cte_est'=0) & (pc'=1) + 0.18947368421052632 : (cte_est'=1) & (pc'=1) + 0.18421052631578946 : (cte_est'=2) & (pc'=1) ;
  [] cte=0  & pc=0 -> 0.20476190476190476 : (cte_est'=-2) & (pc'=1) + 0.17142857142857143 : (cte_est'=-1) & (pc'=1) + 0.18571428571428572 : (cte_est'=0) & (pc'=1) + 0.21904761904761905 : (cte_est'=1) & (pc'=1) + 0.21904761904761905 : (cte_est'=2) & (pc'=1) ;
  [] cte=1  & pc=0 -> 0.20398009950248755 : (cte_est'=-2) & (pc'=1) + 0.24378109452736318 : (cte_est'=-1) & (pc'=1) + 0.16417910447761194 : (cte_est'=0) & (pc'=1) + 0.23383084577114427 : (cte_est'=1) & (pc'=1) + 0.15422885572139303 : (cte_est'=2) & (pc'=1) ;
  [] cte=2  & pc=0 -> 0.215 : (cte_est'=-2) & (pc'=1) + 0.21 : (cte_est'=-1) & (pc'=1) + 0.15 : (cte_est'=0) & (pc'=1) + 0.19 : (cte_est'=1) & (pc'=1) + 0.235 : (cte_est'=2) & (pc'=1) ;

  // Perceiver (HE)
  [] he=-1  & pc=1 -> 0.3395061728395062 : (he_est'=-1) & (pc'=2) + 0.30864197530864196 : (he_est'=0) & (pc'=2) + 0.35185185185185186 : (he_est'=1) & (pc'=2) ;
  [] he=0  & pc=1 -> 0.34971098265895956 : (he_est'=-1) & (pc'=2) + 0.3265895953757225 : (he_est'=0) & (pc'=2) + 0.3236994219653179 : (he_est'=1) & (pc'=2) ;
  [] he=1  & pc=1 -> 0.3242424242424242 : (he_est'=-1) & (pc'=2) + 0.3515151515151515 : (he_est'=0) & (pc'=2) + 0.3242424242424242 : (he_est'=1) & (pc'=2) ;

  // Controller
  [] cte_est=-2 & he_est=-1  & pc=2 -> 1 : (a'=1) & (pc'=3) ;
  [] cte_est=-2 & he_est=0  & pc=2 -> 1 : (a'=1) & (pc'=3) ;
  [] cte_est=-2 & he_est=1  & pc=2 -> 1 : (a'=0) & (pc'=3) ;
  [] cte_est=-1 & he_est=-1  & pc=2 -> 1 : (a'=1) & (pc'=3) ;
  [] cte_est=-1 & he_est=0  & pc=2 -> 1 : (a'=1) & (pc'=3) ;
  [] cte_est=-1 & he_est=1  & pc=2 -> 1 : (a'=0) & (pc'=3) ;
  [] cte_est=0 & he_est=-1  & pc=2 -> 1 : (a'=1) & (pc'=3) ;
  [] cte_est=0 & he_est=0  & pc=2 -> 1 : (a'=0) & (pc'=3) ;
  [] cte_est=0 & he_est=1  & pc=2 -> 1 : (a'=-1) & (pc'=3) ;
  [] cte_est=1 & he_est=-1  & pc=2 -> 1 : (a'=0) & (pc'=3) ;
  [] cte_est=1 & he_est=0  & pc=2 -> 1 : (a'=-1) & (pc'=3) ;
  [] cte_est=1 & he_est=1  & pc=2 -> 1 : (a'=-1) & (pc'=3) ;
  [] cte_est=2 & he_est=-1  & pc=2 -> 1 : (a'=0) & (pc'=3) ;
  [] cte_est=2 & he_est=0  & pc=2 -> 1 : (a'=-1) & (pc'=3) ;
  [] cte_est=2 & he_est=1  & pc=2 -> 1 : (a'=-1) & (pc'=3) ;

  // Dynamics
  [] cte>=-2 & cte<=2 & he>=-1 & he<=1 & pc=3 -> 1 : (he'=he+a) & (cte'=cte+he+a) & (pc'=4) ;

  // Aborter
  [] (cte< -2 | cte>2 | he< -1 | he>1) & pc=4 -> 1 : (pc'=6) ;
  [] cte>=-2 & cte<=2 & he>=-1 & he<=1 & pc=4 -> 1 : (pc'=5) ;



  // loop step
  [] pc=5 & k < N -> 1 : (pc'=0) & (k'=k+1) ;


endmodule
