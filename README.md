# SIMULATE Function Block
### Eventos
INIT: inicialização da FB. Evento de saída associado: INIT_O
RUN: execução da FB. Evento de saída associado: RUN_O
RUN_SIM: executa o modelo de simulacão. Evendo de saída associado: RUN_SIM_O 
### Parâmetros
SIM_TIME: tempo total de simulação. Por norma definido como 1440 (1 dia).
WINDOW: tamanho utilizado para a janela móvel. Esta janela servirá para o cálculo das médias e desvio padrão ao fim de pelo menos 3 rondas.
### Saída
THROUGHPUT: throughput time calculado para a pipeline.
