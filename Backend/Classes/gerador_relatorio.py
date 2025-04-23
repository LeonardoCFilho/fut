class GeradorRelatorios:
    chaves = {
        0: "caminho_yaml", # arquivo .yaml
        1: 'yaml_valido', # True ou False
        2: 'caminho_output', # outup .json
        3: 'tempo_execucao', # em segundos
        4: 'justificativa_arquivo_invalido', # string ou None
        }

    erros_esperados = {'error': [], 'warning': [], 'fatal':[], 'information': []}

    def __init__(self, casos_de_teste : list[dict]):
        self.casos_de_teste_ = casos_de_teste

    # Função que extrai os dados contidos nos arquivos dos resultados esperados (vindos do caso de teste) e os resultados reais (vindos do validador)
    def processarSaidas(self, caminho_saida_esperada:str|pathlib.Path, caminho_saida_real:str|pathlib.Path, yaml_valido:bool)-> list:
        resultados_reais = None
        resultados_esperados = None
        if yaml_valido:
            with open(caminho_saida_real, mode='r', encoding='utf8') as arquivo:
                dicionario_saida_real = json.load(arquivo)

            with open(caminho_saida_esperada, mode="r", encoding="utf8") as arquivo:
                dicionario_saida_esperada = safe_load(arquivo)
            
            resultados_reais :dict = deepcopy(self.erros_esperados)
            for dic in dicionario_saida_real['issue']:
                chave = dic['severity']
                try:
                    resultados_reais[chave].append({dic['code'].lower() : [dic['details']['text'], dic['expression']]})
                except KeyError as err:
                    ...

            resultados_esperados :dict = dicionario_saida_esperada['resultados_esperados']

            # As chaves de ambos precisam ser iguais
            for chave in resultados_esperados.keys():
                # print(chave)
                if chave != 'status':
                    resultados_esperados[chave] = sorted([i.lower() for i in resultados_esperados[chave]])

        return [resultados_reais, resultados_esperados, yaml_valido, caminho_saida_esperada]


    # Função que compara os resultados esperados (vindos do caso de teste) e os resultados reais (vindos do validador)
    def compararResultados(self, tupla_dados: tuple):
        saida_real, saida_esperada, yaml_valido, caminho_yaml, tempo_de_execucao, motivo_da_invalidez = tupla_dados
        copia_saida_real = deepcopy(saida_real)
        copia_saida_esperada = deepcopy(saida_esperada)
        in_congruencias = [[]]
        status = None
        quantidades = None
        quantidades_totais = None
        status_real = None
        status_esperado = None
        if yaml_valido:
            discordancia_vazia = True
            quantidades = deepcopy(self.erros_esperados)
            quantidades_totais = deepcopy(self.erros_esperados)
            # {'error': [], 'warning': [], 'fatal':[], 'information': []}
            for chave in quantidades.keys():
                quantidades[chave] = 0
                quantidades_totais[chave] = len(copia_saida_real[chave])
            status_esperado = copia_saida_esperada['status']
            for chave, valor in copia_saida_esperada.items():
                if chave != 'status':
                    for v_esperada in valor:
                        for index, v_real in enumerate(copia_saida_real[chave]):
                            v_temp = list(v_real.keys())[0] == v_esperada
                            if v_temp:
                                in_congruencias[0].append([chave, v_esperada, list(copia_saida_real[chave].pop(index).values())[0], 0])
                                quantidades[chave] += 1
                                break
                        else:
                            in_congruencias[0].append([chave, v_esperada, False, 0])
                            discordancia_vazia = False

            for chave, valor in copia_saida_real.items():
                for v_real in valor:
                    discordancia_vazia = False
                    in_congruencias[0].append([chave, list(v_real.keys())[0], list(v_real.values())[0], 1])

            maximo = max(quantidades.values())
            status_possiveis = [i for i in quantidades.keys() if quantidades[i] == maximo]

            if not any(i in status_possiveis for i in ('error', 'fatal')) and status_esperado.strip() == 'success':
                status_real = 'success'
            else:
                status_real = next((item for item in status_possiveis if item in ('fatal', 'error', 'warning', 'information')), None)
            
            if status_real != status_esperado.strip():
                status = False
            elif status_real == status_esperado and discordancia_vazia:
                status = True
            else:
                status = False
        return in_congruencias + [yaml_valido, tempo_de_execucao, status, status_esperado, status_real, caminho_yaml, quantidades, quantidades_totais, motivo_da_invalidez]

    # Função que gera os relatórios unitários e o relatório final
    def gerarRelatorios(self):

        relatorios = {}
        relatorio_unitario = {
            'status' : None,
            'yaml_valido' : None,
            'motivo_da_invalidez': None,
            'tempo_de_execucao' : None,
            'correspondencia': [],
            'status_real': None,
            'status_esperado': None,
            'discordancia':
                    {
                        'issue_esperada_ausente_no_real' : [],
                        'issue_real_ausente_na_esperada' : [],
                    },
        }
        copia_relatorio_unitario = deepcopy(relatorio_unitario)
        resultados = map(
            self.compararResultados,
            [
                self.processarSaidas(dicionario[self.chaves[0]], dicionario[self.chaves[2]], dicionario[self.chaves[1]] ) + [dicionario[self.chaves[3]], dicionario[self.chaves[4]]]
                for dicionario in self.casos_de_teste_
            ]
        )
        issues_corretas = {}
        issues_reais = {}
        for chave in self.erros_esperados.keys():
            issues_corretas[f"%_{chave}_reais_acertados"] = 0
            issues_reais[f"quantidade_{chave}_reais_totais"] = 0

        for relat in resultados:
            in_congruencias, yaml_valido, tempo_de_execucao, status, status_esperado, status_real, caminho_yaml, quantidades, quantidades_totais, motivo_da_invalidez, = relat
            relatorio_unitario['yaml_valido'] = yaml_valido
            relatorio_unitario['motivo_da_invalidez'] = motivo_da_invalidez
            if yaml_valido:
                relatorio_unitario['status_esperado'] = status_esperado
                relatorio_unitario['tempo_de_execucao'] = tempo_de_execucao
                relatorio_unitario['status'] = status
                relatorio_unitario['status_esperado'] = status_esperado
                relatorio_unitario['status_real'] = status_real
                for item in in_congruencias:
                    if item[2] and item[3] == 0:
                        relatorio_unitario['correspondencia'].append({'tipo':item[0], 'codigo':item[1], 'descricao': item[2][0], 'local': item[2][1]})
                    elif not item[2] and item[3] == 0:
                        relatorio_unitario['discordancia']['issue_esperada_ausente_no_real'].append({'tipo':item[0], 'codigo':item[1], 'descricao': None, 'local': None})
                    elif item[3] == 1:
                        relatorio_unitario['discordancia']['issue_real_ausente_na_esperada'].append({'tipo':item[0], 'codigo':item[1], 'descricao': item[2][0], 'local': item[2][1]})
                
                for chave in self.erros_esperados.keys():
                    issues_corretas[f"%_{chave}_reais_acertados"] += quantidades[chave]
                    issues_reais[f"quantidade_{chave}_reais_totais"] += quantidades_totais[chave]

            relatorios[str(caminho_yaml)] = relatorio_unitario
            relatorio_unitario = deepcopy(copia_relatorio_unitario)

        issue_correta_soma_parcial = max(sum(issues_corretas.values()),1)

        tempo_total = sum([i['tempo_de_execucao'] for i in relatorios.values() if i['yaml_valido']])
        numero_de_testes_validos = len([0 for i in relatorios.values() if i['yaml_valido']])

        for chave in self.erros_esperados.keys():
            issues_corretas[f"%_{chave}_reais_acertados"] =  round(issues_corretas[f"%_{chave}_reais_acertados"]/issue_correta_soma_parcial,2)
        
        relatorio_final = {
            'numero_de_testes_validos': numero_de_testes_validos,
            'numeros_de_testes_totais' : len(relatorios),
            'tempo_total': tempo_total,
            'tempo_medio': round(tempo_total/numero_de_testes_validos,1),
            'data': datetime.now().strftime("%Y/%m/%d - %H:%M")
        }
        relatorio_final.update(issues_reais)
        relatorio_final.update(issues_corretas)
        relatorios['relatorio_final'] = relatorio_final
        return relatorios

    # Função recebe os dados de compararResultados() e cria um relatório .json do caso de teste
    def gerarRelatorioJson(self):
        relatorios = self.gerarRelatorios()
        json_valido = json.dumps(relatorios, indent=4, ensure_ascii=False)

        with open(pathlib.Path.cwd() / 'relatorio_final_fut.json', mode='w', encoding='utf8') as arquivo:
            arquivo.write(json_valido)

        rmtree(pathlib.Path().cwd() / '.temp-fut', ignore_errors=True)

    @classmethod
    def modificarChaves(cls, novas_chaves:dict):
        cls.chaves = novas_chaves

    @classmethod
    def modificarErrosEsperados(cls, novos_erros_esperados:dict):
        cls.erros_esperados = novos_erros_esperados
