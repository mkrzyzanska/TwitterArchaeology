data{
    int<lower=1> N; // number of observations
    array[N] int R;
    array[N] int F;
    vector[N] S; // continuous predictor variable between -1 and 1
    int<lower=1> T; // number of topics
    array[N] int topics;     
    int<lower=1> U; // number of user categories
    array[N] int users; 
    array[N] int TL;
    int<lower=1> L;
    vector[L-1] alphaD;

}
parameters{
     vector[T] alpha_topic; // coefficients for each topic
     vector[U] alpha_user; //coefficients for each user category
     real alpha_bar;
     real ap;
     real bp;
     real bF;
     real bS;
     real <lower=0> sigma_topic;
     real <lower=0> sigma_user;
     real bT;
     simplex[L-1] delta;
}
model{
     vector[N] p;
     vector[N] lambda;
     vector[L] delta_j;
     delta ~ dirichlet( alphaD );
     delta_j = append_row(0, delta);
     alpha_bar ~ normal(3,1); // make sure to allow intercepts to vary considerably, but not overlap with 0
     alpha_topic ~ normal(alpha_bar, sigma_topic);
     alpha_user ~ normal(0,sigma_user);
     bF ~ normal( 0 , 0.2 );
     bT ~ normal( 0 , 0.2 );
     bS ~ normal( 0 , 0.2 );
     bp ~ normal( 1 , 0.5 );
     ap ~ normal( -1.5 , 1 );
     sigma_topic ~ cauchy(0,0.5);
     sigma_user ~ cauchy(0,0.5);
    for ( i in 1:N ) {
        lambda[i] = alpha_topic[topics[i]] + alpha_user[users[i]]+bS*S[i]+bF*F[i]+bT*sum(delta_j[1:TL[i]]);
        lambda[i] = exp(lambda[i]);
    }
    for ( i in 1:N ) {
        p[i] = ap + bp*F[i];
        p[i] = inv_logit(p[i]);
    }
    for ( i in 1:N ) {
        if ( R[i]==0 )
            target += log_mix( p[i] , 0 , poisson_lpmf(0|lambda[i]) );
        if ( R[i] > 0 )
            target += log1m( p[i] ) + poisson_lpmf(R[i] | lambda[i] );
    }
}

