---
title: Félicité Smart Data Services - 2023
publishDate: 2023-12-15 00:00:00
img: /portfolio/assets/U2P-Platform.jpg
img_alt: Application WebGl Félicité
description: |
  Pour représenter en 3D les divers espaces d'une grande structure, j'ai travaillé sur un outil qui permet de séparer les différentes parties d'un gros bâtiment
  en plusieurs blocs, qui chacun comporte des étages. Chaque étage est ensuite "ouvrable" pour voir apparaitre les différentes pièces et afficher des valeurs de températures, luminosité, energie, ... avec des codes couleurs préétablis.
tags:
  - Unity
  - WebGL
  - AssetBundles
  - Javascript
  - JSON
---

L’application <a href ="https://felicite-sds.opencaps.io/login-sso" target="_blank">Félicité Smart Data Services</a> déveoppé par 
<a href="https://www.opencaps.io/" target="_blank"> OpenCaps </a> permet de naviguer au sein d'un ensemble de bâtiments appelé "Félicité".
Je me suis occupé de la partie 3D de cette navigation, réalisée avec Unity en WebGl et qui s'intègre dans un site réalisé avec VueJS.
Une communication a été mise en place avec des message JSON entre Unity et VueJS pour recevoir les données à afficher et réagir aux interractions de l'utilisateur.

<div>
  <p>
    <ul>
      <li>Gestion de la caméra pour tourner, zoomer, ou forcer certaines vues
      <li>La caméra cible automatiquent le bloc sélectionné de manière fluide
      <li>Définition et ouverture des blocs du bâtiment grâce à des fichiers JSON
      <li>Etiquettes montrant les informations des blocs au survol
      <li>Coloration des blocs ou des espaces suivant les données reçues
      <li>Eclairage simulant le soleil en fonction de l'heure des données
      <li>Gestion des AssetBundles pour télécharger les objets des étages
    </ul>
  </p>
</div>
