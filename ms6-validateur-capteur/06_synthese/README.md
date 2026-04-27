# 06_synthese — synthese_avant_apres.pdf (livrable obligatoire 2 pages)

## Generation rapide (sans Python)

1. Recuperer les captures `sonar_avant.png` et `sonar_apres.png` depuis le dashboard SonarCloud,
   les deposer dans `04_analyse_avant/` et `05_analyse_apres/` respectivement.
2. Remplir les `__a remplir__` du fichier `synthese_avant_apres.html` avec les vrais chiffres
   lus dans les rapports `flake8_*.txt`, `snyk_*.txt`, `rapport_tests.txt` et le dashboard SonarCloud.
3. Ouvrir `synthese_avant_apres.html` dans un navigateur (Chrome / Edge).
4. **Ctrl+P** -> Destination : "Enregistrer au format PDF" -> Marges : "Aucune" -> Cocher "Arriere-plans" ->
   Enregistrer sous `synthese_avant_apres.pdf` (toujours dans `06_synthese/`).
5. Verifier que le PDF fait bien **2 pages exactement**.

## Generation alternative (Python avec WeasyPrint si dispo)

```bash
pip install weasyprint
weasyprint synthese_avant_apres.html synthese_avant_apres.pdf
```

## Contenu attendu (rappel sujet EC03 page 10)

### Page 1
- Captures SonarCloud AVANT et APRES cote a cote
- Metriques comparees (bugs, code smells, dette technique, coverage)
- Tableau Snyk : CVE | gravite | package | version vulnerable | version corrigee | action appliquee

### Page 2
- Analyse des balises SonarCloud High / Critical : nom + fichier:ligne + cause + correction OU dette justifiee
- Bilan : nombre d'alertes avant/apres, vulnerabilites traitees vs residuelles
