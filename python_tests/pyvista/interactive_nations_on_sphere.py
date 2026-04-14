import pyvista as pv
import numpy as np
from scipy.spatial import cKDTree

def main():
    # Creiamo una sfera ad alta risoluzione
    sphere = pv.Sphere(radius=1.0, theta_resolution=1200, phi_resolution=1200)
    
    # Memorizziamo i centri di ciascuna cella (tasselli sferici)
    cell_centers = sphere.cell_centers().points

    # Manteniamo una lista dinamica per le "capitali" delle nazioni
    capitals = []
    
    # Inizializziamo l'array dei paesi (all'inizio tutte le celle appartengono 
    # alla nazione 0, ovvero l'oceano o il "nulla")
    sphere.cell_data["Nation"] = np.zeros(sphere.n_cells)
    
    plotter = pv.Plotter()

    # Aggiungiamo la mesh alla scena
    mesh_actor = plotter.add_mesh(
        sphere,
        scalars="Nation",
        cmap="tab20",           # Tavolozza con molti colori distinti
        clim=[0, 20],          # Range fisso: evita che si blocchi su [0,0] all'avvio
        show_scalar_bar=False,
        show_edges=False       # Nessuna griglia visibile
    )
    
    # Useremo questo per tracciare i punti rossi
    points_actor = None
    
    def update_nations():
        nonlocal points_actor
        
        if not capitals:
            return
            
        # 1. Ricostruiamo le aree di Voronoi
        pts = np.array(capitals)
        tree = cKDTree(pts)
        _, nation_ids = tree.query(cell_centers)
        
        # 2. Aggiorniamo gli scalari sulla sfera (1-indexed per distinguerli dallo 0)
        sphere.cell_data["Nation"] = nation_ids + 1
        
        # 3. Aggiorniamo i punti rossi
        if points_actor is not None:
            plotter.remove_actor(points_actor)
            
        points_actor = plotter.add_points(
            pts, 
            color='red', 
            point_size=15, 
            render_points_as_spheres=True
        )

        # 4. Ridisegniamo dopo aver aggiornato sia i colori che i punti
        plotter.render()

    # Callback attivata al clic sinistro del mouse sulla superficie
    def on_click(point):
        # 'point' è un array numpy [x, y, z] del punto sulla superficie cliccato
        if point is not None:
            pt = np.array(point)
            
            # Normalizziamo per assicurarci che giaccia sulla sfera (raggio = 1.0)
            length = np.linalg.norm(pt)
            if length > 0:
                pt = pt / length
                
            capitals.append(pt)
            print(f"Nazione aggiunta in: {pt}")
            update_nations()

    # enable_surface_point_picking si attiva con CLICK SINISTRO del mouse
    # (enable_cell_picking invece richiedeva il tasto 'P' da tastiera)
    plotter.enable_surface_point_picking(
        callback=on_click,
        show_message=False,
        show_point=False,       # non mostrare il pallino giallo di default
        pickable_window=False   # solo sulla mesh, non su sfondo
    )
    
    # Inizializziamo con 3 nazioni casuali (opzionale)
    phi = np.random.uniform(0, np.pi, 3)
    theta = np.random.uniform(0, 2 * np.pi, 3)
    for p, t in zip(phi, theta):
        capitals.append([
            np.sin(p) * np.cos(t),
            np.sin(p) * np.sin(t),
            np.cos(p)
        ])
    update_nations()

    plotter.add_text("Clicca sulla sfera per aggiungere una nazione!", font_size=14)
    plotter.show()

if __name__ == '__main__':
    main()
