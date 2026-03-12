import pygame
import numpy as np
import sys
import os
from pathlib import Path

#site para guardar seu fdp 
#https://phet.colorado.edu/pt_BR/simulations/quantum-tunneling
#https://www.scielo.br/j/rbef/a/74TLMRVPDDNBrj7jRKQxRHJ/?lang=pt
#https://www.scielo.br/j/rbef/a/V7Sz8cmP7GBvVPPwTLqRpLt/?lang=pt
#https://www.scielo.br/j/rbef/a/3w3WfZMd5TCqhdjFRC4qKPS/?format=html&lang=pt
#https://www.scielo.br/j/rbef/a/jLCKzgvbHSg96RM9Twc3PDm/?lang=pt

LARGURA, ALTURA = 1200, 700
FPS = 60

hbar = 1.0  
c_light = 137.0 

class LabUniversalFinal:
    def __init__(self, massa_tipo="eletron", modo_potencial=1):
        self.x = np.linspace(-15, 15, 1000)
        self.tempo = 0
        self.time_multiplier = 1 
        self.massa_tipo = massa_tipo
        self.modo_potencial = modo_potencial
        
        #M = massa de repouso
        self.m = 1.0 if massa_tipo == "eletron" else 1836.0 
        self.E_base = 5.0 
        self.V0 = 6.5 
        
        #MORSE
        self.De, self.re, self.a = 8.0, 0.0, 0.4
        
        self.temperatura = 0 
        self.voltagem = 0.0 
        
        self.testes_totais = 0
        self.sucessos_totais = 0
        self.deteccoes = []
        self.ja_disparou = False
        self.historico_energia = []

    def salvar_experimento(self, tela):
        """Exporta Log TXT"""
        path_downloads = str(Path.home() / "Downloads")
        timestamp = pygame.time.get_ticks()
        
        img_nome = f"Quantum_Graph_{timestamp}.png"
        pygame.image.save(tela, os.path.join(path_downloads, img_nome))
        
        log_nome = f"Quantum_Log_{timestamp}.txt"
        tx = (self.sucessos_totais/self.testes_totais*100) if self.testes_totais > 0 else 0
        modo_str = "BARREIRA" if self.modo_potencial == 1 else "MORSE-DIRAC"
        
        with open(os.path.join(path_downloads, log_nome), "w") as f:
            f.write(f"EXPERIMENTO QUANTICO \n")
            f.write(f"Modo: {modo_str} | Particula: {self.massa_tipo}\n")
            f.write(f"Massa (m): {self.m} | Voltagem: {self.voltagem}V\n")
            f.write(f"Temperatura: {self.temperatura}K\n")
            f.write(f"Taxa de Tunelamento: {tx:.6f}%\n")
            f.write(f"Amostras: {self.testes_totais}\n")        
        print(f"Dados salvos")

    def calcular_potencial_completo(self, x_pos, ruido_t=0):
        v_eletrico = -self.voltagem * x_pos * 0.15
        if self.modo_potencial == 1:
            v_classico = np.zeros_like(x_pos)
            v_classico[(x_pos > 2.0) & (x_pos < 3.5)] = self.V0
            return v_classico + v_eletrico + (ruido_t * 5)
        else:
            v_morse = self.De * (1 - np.exp(-self.a * (x_pos - self.re)))**2
            return v_morse + v_eletrico + (ruido_t * 10)

    def calcular_fisica(self):
        #Incerteza
        ruido_incerteza = np.random.normal(0, 0.05) 
        jitter_energia = np.random.normal(0, 0.01) * self.E_base
        
        if self.modo_potencial == 1:
            # SCHRÖDINGER
            energia_t = self.E_base + (self.voltagem * 0.5) + jitter_energia
            k0 = np.sqrt(2 * self.m * max(0.1, energia_t)) / hbar
            v_grupo = k0 * hbar / self.m
            pos_c = -11.0 + (v_grupo * self.tempo)
            sigma_t = 1.2 * np.sqrt(1 + ((hbar * self.tempo) / (self.m * 1.2**2))**2)
            envelope = np.exp(-(self.x - pos_c)**2 / (2 * sigma_t**2))
            fase = (k0 + ruido_incerteza) * self.x - (energia_t * self.tempo) / hbar
            psi = envelope * np.exp(1j * fase)
        else:
            #Dirac 
            p_base = np.sqrt(2 * self.m * 5.0) / c_light
            p_efetivo = p_base + (self.voltagem * 0.2)
            energia_repouso = self.m * (c_light**2)
            energia_t = np.sqrt((p_efetivo * c_light)**2 + energia_repouso**2) + jitter_energia  #https://phet.colorado.edu/pt_BR/simulations/quantum-tunneling
            v_rel = (p_efetivo * c_light**2) / energia_t
            pos_c = -10.0 + (v_rel * self.tempo)
            sigma_t = 0.8 * np.sqrt(1 + (self.tempo/(self.m*0.1))**2)
            envelope = np.exp(-(self.x - pos_c)**2 / (2 * sigma_t**2))
            # Zitterbewegung
            tremor = 0.15 * np.sin(c_light**2 * self.tempo * 0.1)
            fase = (p_efetivo * self.x - energia_t * self.tempo) / hbar
            psi = envelope * np.exp(1j * (fase + tremor + ruido_incerteza))

        e_plot = energia_t / (1e4 if self.modo_potencial == 2 else 1)
        self.historico_energia.append(e_plot)
        if len(self.historico_energia) > 180: self.historico_energia.pop(0)
        return psi / np.linalg.norm(psi), pos_c, energia_t

def principal():
    pygame.init()
    tela = pygame.display.set_mode((LARGURA, ALTURA))
    pygame.display.set_caption("Quantum Lab v12.3 - Downloads Enabled")
    fonte = pygame.font.SysFont("Consolas", 15)
    sim = LabUniversalFinal("eletron", 1)
    relogio = pygame.time.Clock()

    while True:
        tela.fill((3, 3, 12))
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT: pygame.quit(); sys.exit()
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_1: sim = LabUniversalFinal(sim.massa_tipo, 1)
                if ev.key == pygame.K_2: sim = LabUniversalFinal(sim.massa_tipo, 2)
                if ev.key == pygame.K_e: sim = LabUniversalFinal("eletron", sim.modo_potencial)
                if ev.key == pygame.K_p: sim = LabUniversalFinal("proton", sim.modo_potencial)
                if ev.key == pygame.K_UP: sim.time_multiplier = min(200, sim.time_multiplier + 10)
                if ev.key == pygame.K_DOWN: sim.time_multiplier = max(1, sim.time_multiplier - 10)
                if ev.key == pygame.K_v: sim.voltagem += 0.5
                if ev.key == pygame.K_c: sim.voltagem -= 0.5
                if ev.key == pygame.K_t: sim.temperatura = min(10000, sim.temperatura + 500)
                if ev.key == pygame.K_g: sim.temperatura = max(0, sim.temperatura - 500)
                if ev.key == pygame.K_k: sim.salvar_experimento(tela) # EXPORTAR
                if ev.key == pygame.K_r: sim.__init__(sim.massa_tipo, sim.modo_potencial)

        sim.tempo += 0.01 * sim.time_multiplier
        psi, pos_c, e_atual = sim.calcular_fisica()
        
        base_y = 500 if sim.modo_potencial == 1 else 450
        escala_x, escala_y = (35, 40) if sim.modo_potencial == 1 else (40, 25)

        if sim.modo_potencial == 1:
            bx, bw = 600 + 2.0*escala_x, (3.5 - 2.0)*escala_x
            by_topo = base_y - (sim.V0 + (-sim.voltagem*2.75*0.15))*escala_y
            pygame.draw.rect(tela, (40, 20, 60), (bx, by_topo, bw, sim.V0*escala_y))
            pygame.draw.rect(tela, (255, 100, 100), (bx, by_topo, bw, sim.V0*escala_y), 2)
        else:
            pts_pot = [(600 + xi*escala_x, base_y - sim.calcular_potencial_completo(xi)*escala_y) for xi in sim.x]
            pygame.draw.lines(tela, (150, 150, 150), False, pts_pot, 2)

        prob_vis = np.abs(psi)**2 * (15000 if sim.modo_potencial == 1 else 40000)
        pts_onda = [(600 + xi*escala_x, (base_y - (-sim.voltagem * xi * 0.15 * escala_y)) - prob_vis[i]) for i, xi in enumerate(sim.x)]
        pygame.draw.lines(tela, (0, 255, 255), False, pts_onda, 2)

        pygame.draw.rect(tela, (10, 10, 30), (950, 50, 200, 120))
        pygame.draw.rect(tela, (200, 200, 200), (950, 50, 200, 120), 1)
        if len(sim.historico_energia) > 1:
            pts_e = [(950 + i, 160 - (v - sim.historico_energia[0])*20 - 50) for i, v in enumerate(sim.historico_energia)]
            pygame.draw.lines(tela, (0, 255, 150), False, pts_e, 1)

        if pos_c >= (1.5 if sim.modo_potencial == 1 else -2.0) and not sim.ja_disparou:
            prob = np.abs(psi)**2
            indices = np.random.choice(len(sim.x), size=2000, p=prob/prob.sum())
            for idx in indices:
                px = sim.x[idx]
                sucesso = px > (3.5 if sim.modo_potencial == 1 else 5.0)
                if sucesso: sim.sucessos_totais += 1
                sim.testes_totais += 1
                if len(sim.deteccoes) < 150: sim.deteccoes.append({'x': px, 'v': sim.calcular_potencial_completo(px), 'ok': sucesso})
            sim.ja_disparou = True
        
        if pos_c > 14: sim.tempo = 0; sim.ja_disparou = False; sim.deteccoes = []
        for d in sim.deteccoes:
            pygame.draw.circle(tela, (0, 255, 100) if d['ok'] else (180, 180, 180), (int(600+d['x']*escala_x), int(base_y - d['v']*escala_y)), 2)

        txt_e = f"{e_atual/1e4:.2f}e4 eV" if sim.modo_potencial == 2 else f"{e_atual:.2f} eV"
        hud = [
            (f"MODO: {'BARREIRA' if sim.modo_potencial==1 else 'MORSE-DIRAC'}", (255, 215, 0)),
            (f"PARTICULA: {sim.massa_tipo.upper()}", (255,255,255)),
            (f"VOLTAGEM: {sim.voltagem}V", (255,255,255)),
            (f"ENERGIA: {txt_e}", (0, 255, 255)),
            (f"TAXA: {(sim.sucessos_totais/sim.testes_totais*100 if sim.testes_totais>0 else 0):.3f}%", (200, 255, 200)),
            (f"[K] SALVAR LOG E GRAFICO EM DOWNLOADS", (255, 100, 255))
        ]
        for i, (t, c) in enumerate(hud): tela.blit(fonte.render(t, True, c), (20, 30 + i*22))
        pygame.display.flip()
        relogio.tick(FPS)

if __name__ == "__main__": principal()