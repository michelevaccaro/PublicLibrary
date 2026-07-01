/* ==========================================================================
   NovaLuce Energia — Translation dictionary (IT / EN / FR / ES)
   Official Italian process names (e.g. "Voltura", "Autolettura", "Switch")
   are never translated — they are the actual regulatory/process terms.
   Everything else (chrome, descriptions, buttons) is translated.
   ========================================================================== */

var NL_LANGS = ["it", "en", "fr", "es"];

var NL_I18N = {
  /* ---------- Navigation ---------- */
  "nav.home": { it: "Home", en: "Home", fr: "Accueil", es: "Inicio" },
  "nav.becomeCustomer": { it: "Diventa Cliente", en: "Become a Customer", fr: "Devenir client", es: "Hazte cliente" },
  "nav.customerArea": { it: "Area Clienti", en: "Customer Area", fr: "Espace Client", es: "Área de Clientes" },
  "nav.login": { it: "Accedi", en: "Log In", fr: "Se connecter", es: "Acceder" },
  "nav.logout": { it: "Esci", en: "Log Out", fr: "Se déconnecter", es: "Salir" },
  "brand.tagline": { it: "Energia", en: "Energy", fr: "Énergie", es: "Energía" },

  /* ---------- Home / hero ---------- */
  "hero.eyebrow": { it: "100% energia da fonti rinnovabili", en: "100% energy from renewable sources", fr: "100 % d'énergie d'origine renouvelable", es: "100% energía de fuentes renovables" },
  "hero.title": { it: "Energia semplice, trasparente, ogni giorno.", en: "Simple, transparent energy, every day.", fr: "Une énergie simple et transparente, au quotidien.", es: "Energía simple y transparente, cada día." },
  "hero.lead": { it: "NovaLuce Energia fornisce luce e gas a case e imprese in tutta Italia, con tariffe chiare, assistenza dedicata e tutti i servizi gestibili online, in pochi click.", en: "NovaLuce Energia supplies electricity and gas to homes and businesses across Italy, with clear rates, dedicated support and every service manageable online in just a few clicks.", fr: "NovaLuce Energia fournit l'électricité et le gaz aux particuliers et aux entreprises dans toute l'Italie, avec des tarifs clairs, une assistance dédiée et tous les services gérables en ligne en quelques clics.", es: "NovaLuce Energia suministra luz y gas a hogares y empresas en toda Italia, con tarifas claras, atención dedicada y todos los servicios gestionables online en pocos clics." },
  "hero.ctaLogin": { it: "Accedi all'Area Clienti", en: "Log in to the Customer Area", fr: "Accéder à l'Espace Client", es: "Acceder al Área de Clientes" },
  "hero.stat1Label": { it: "Clienti serviti", en: "Customers served", fr: "Clients servis", es: "Clientes atendidos" },
  "hero.stat2Label": { it: "Energia verde certificata", en: "Certified green energy", fr: "Énergie verte certifiée", es: "Energía verde certificada" },
  "hero.stat3Label": { it: "Assistenza online", en: "Online support", fr: "Assistance en ligne", es: "Asistencia online" },
  "hero.cardTitle": { it: "La tua fornitura in un colpo d'occhio", en: "Your supply at a glance", fr: "Votre contrat en un coup d'œil", es: "Tu suministro de un vistazo" },
  "hero.cardConsumptionLabel": { it: "Consumo stimato mensile", en: "Estimated monthly consumption", fr: "Consommation mensuelle estimée", es: "Consumo mensual estimado" },
  "hero.cardNextBillLabel": { it: "Prossima bolletta", en: "Next bill", fr: "Prochaine facture", es: "Próxima factura" },
  "hero.cardPaymentLabel": { it: "Modalità pagamento", en: "Payment method", fr: "Mode de paiement", es: "Método de pago" },
  "hero.cardOriginLabel": { it: "Origine energia", en: "Energy source", fr: "Origine de l'énergie", es: "Origen de la energía" },
  "hero.cardOriginTag": { it: "Rinnovabile", en: "Renewable", fr: "Renouvelable", es: "Renovable" },

  /* ---------- Quick links ---------- */
  "quicklinks.eyebrow": { it: "Link Rapidi", en: "Quick Links", fr: "Liens rapides", es: "Enlaces rápidos" },
  "quicklinks.title": { it: "Vai dritto alla procedura che ti serve", en: "Go straight to the process you need", fr: "Accédez directement à la démarche dont vous avez besoin", es: "Ve directo al trámite que necesitas" },
  "quicklinks.subtitle": { it: "Le operazioni più richieste, a portata di click.", en: "The most requested operations, one click away.", fr: "Les opérations les plus demandées, à portée de clic.", es: "Las operaciones más solicitadas, a un clic." },

  /* ---------- Features ---------- */
  "features.eyebrow": { it: "Perché sceglierci", en: "Why choose us", fr: "Pourquoi nous choisir", es: "Por qué elegirnos" },
  "features.title": { it: "Tutto quello che serve, senza sorprese", en: "Everything you need, no surprises", fr: "Tout ce qu'il faut, sans surprises", es: "Todo lo que necesitas, sin sorpresas" },
  "features.subtitle": { it: "Gestione digitale del contratto, tariffe trasparenti e un'assistenza pensata per farti risparmiare tempo.", en: "Digital contract management, transparent rates and support designed to save you time.", fr: "Gestion numérique du contrat, tarifs transparents et une assistance pensée pour vous faire gagner du temps.", es: "Gestión digital del contrato, tarifas transparentes y una atención pensada para ahorrarte tiempo." },
  "features.card1Title": { it: "Tariffe trasparenti", en: "Transparent rates", fr: "Tarifs transparents", es: "Tarifas transparentes" },
  "features.card1Desc": { it: "Nessun costo nascosto: prezzo dell'energia chiaro fin dal preventivo, sia per la luce che per il gas.", en: "No hidden costs: clear energy pricing from the quote onward, for both electricity and gas.", fr: "Aucun coût caché : un prix de l'énergie clair dès le devis, pour l'électricité comme pour le gaz.", es: "Sin costes ocultos: precio de la energía claro desde el presupuesto, tanto para luz como para gas." },
  "features.card2Title": { it: "Tutto online", en: "Everything online", fr: "Tout en ligne", es: "Todo online" },
  "features.card2Desc": { it: "Autolettura, bolletta web, domiciliazione e molto altro: gestisci la tua fornitura dall'Area Clienti, 24 ore su 24.", en: "Meter readings, paperless billing, direct debit and more: manage your supply from the Customer Area, 24/7.", fr: "Relevé de compteur, facture dématérialisée, prélèvement automatique et bien plus : gérez votre contrat depuis l'Espace Client, 24h/24.", es: "Autolectura, factura web, domiciliación y mucho más: gestiona tu suministro desde el Área de Clientes, las 24 horas." },
  "features.card3Title": { it: "Assistenza dedicata", en: "Dedicated support", fr: "Assistance dédiée", es: "Atención dedicada" },
  "features.card3Desc": { it: "Un servizio clienti pronto ad aiutarti in ogni fase: dalla richiesta di attivazione alla gestione quotidiana.", en: "A customer service team ready to help at every step: from activation requests to day-to-day management.", fr: "Un service client prêt à vous aider à chaque étape : de la demande d'activation à la gestion quotidienne.", es: "Un servicio de atención listo para ayudarte en cada etapa: desde la solicitud de activación hasta la gestión diaria." },

  /* ---------- Split section ---------- */
  "split.eyebrow1": { it: "Per la casa e per il business", en: "For home and business", fr: "Pour la maison et l'entreprise", es: "Para el hogar y la empresa" },
  "split.title1": { it: "Un'unica energia, due mondi da servire", en: "One energy, two worlds to serve", fr: "Une seule énergie, deux mondes à servir", es: "Una sola energía, dos mundos que atender" },
  "split.desc1": { it: "Che tu sia un privato o un'azienda con Partita IVA, NovaLuce Energia ti accompagna dalla prima attivazione alla gestione quotidiana del contratto.", en: "Whether you're a private individual or a business with a VAT number, NovaLuce Energia supports you from first activation to day-to-day contract management.", fr: "Que vous soyez un particulier ou une entreprise avec un numéro de TVA, NovaLuce Energia vous accompagne de la première activation à la gestion quotidienne du contrat.", es: "Ya seas un particular o una empresa con NIF/IVA, NovaLuce Energia te acompaña desde la primera activación hasta la gestión diaria del contrato." },
  "split.li1a": { it: "Attivazione rapida per nuove forniture e subentri", en: "Fast activation for new supplies and reactivations", fr: "Activation rapide pour les nouvelles fournitures et les reprises", es: "Activación rápida para nuevos suministros y reactivaciones" },
  "split.li1b": { it: "Switch guidato dal tuo attuale fornitore, senza interruzioni", en: "Guided switch from your current supplier, with no interruption", fr: "Changement guidé depuis votre fournisseur actuel, sans interruption", es: "Cambio guiado desde tu proveedor actual, sin interrupciones" },
  "split.li1c": { it: "Fatturazione elettronica e bolletta web inclusa", en: "Electronic invoicing and paperless billing included", fr: "Facturation électronique et facture dématérialisée incluses", es: "Facturación electrónica y factura web incluidas" },
  "split.li1d": { it: "Assistenza su voltura, disdetta e rimborsi", en: "Support for holder changes, termination and refunds", fr: "Assistance pour les changements de titulaire, résiliations et remboursements", es: "Asistencia para cambios de titular, bajas y reembolsos" },
  "split.cta1": { it: "Scopri come diventare cliente", en: "Discover how to become a customer", fr: "Découvrez comment devenir client", es: "Descubre cómo hacerte cliente" },
  "split.eyebrow2": { it: "Sei già nostro cliente?", en: "Already a customer?", fr: "Déjà client ?", es: "¿Ya eres cliente?" },
  "split.title2": { it: "Gestisci tutto dall'Area Clienti", en: "Manage everything from the Customer Area", fr: "Gérez tout depuis l'Espace Client", es: "Gestiona todo desde el Área de Clientes" },
  "split.desc2": { it: "Autolettura, domiciliazione SEPA, estratto conto, voltura, disdetta e altri 9 servizi disponibili in pochi click, in totale autonomia.", en: "Meter readings, SEPA direct debit, account statements, holder changes, termination and 9 more services available in just a few clicks, fully on your own.", fr: "Relevé de compteur, prélèvement SEPA, relevé de compte, changement de titulaire, résiliation et 9 autres services disponibles en quelques clics, en toute autonomie.", es: "Autolectura, domiciliación SEPA, extracto de cuenta, cambio de titular, baja y otros 9 servicios disponibles en pocos clics, con total autonomía." },
  "split.li2a": { it: "Invia l'autolettura del tuo contatore", en: "Submit your meter reading", fr: "Envoyez le relevé de votre compteur", es: "Envía la autolectura de tu contador" },
  "split.li2b": { it: "Attiva la domiciliazione bancaria SEPA", en: "Set up SEPA direct debit", fr: "Activez le prélèvement bancaire SEPA", es: "Activa la domiciliación bancaria SEPA" },
  "split.li2c": { it: "Richiedi estratto conto e conferme di pagamento", en: "Request account statements and payment confirmations", fr: "Demandez des relevés de compte et des confirmations de paiement", es: "Solicita extractos de cuenta y confirmaciones de pago" },
  "split.li2d": { it: "Gestisci voltura, recesso e rimborsi", en: "Manage holder changes, termination and refunds", fr: "Gérez les changements de titulaire, résiliations et remboursements", es: "Gestiona cambios de titular, bajas y reembolsos" },

  /* ---------- CTA banner ---------- */
  "ctaBanner.title": { it: "Pronto a passare a un'energia più semplice?", en: "Ready to switch to simpler energy?", fr: "Prêt à passer à une énergie plus simple ?", es: "¿Listo para pasarte a una energía más sencilla?" },
  "ctaBanner.desc": { it: "Richiedi l'attivazione: ti guidiamo passo dopo passo nella procedura corretta per il tuo caso.", en: "Request activation: we'll guide you step by step through the right process for your situation.", fr: "Demandez l'activation : nous vous guidons pas à pas dans la procédure adaptée à votre situation.", es: "Solicita la activación: te guiamos paso a paso en el trámite adecuado para tu caso." },
  "ctaBanner.button": { it: "Vai alle procedure per nuovi clienti", en: "Go to procedures for new customers", fr: "Voir les démarches pour les nouveaux clients", es: "Ir a los trámites para nuevos clientes" },

  /* ---------- Footer ---------- */
  "footer.tagline": { it: "Fornitore di energia elettrica e gas naturale. Demo di prodotto — dati e contenuti non reali.", en: "Electricity and natural gas supplier. Product demo — data and content are not real.", fr: "Fournisseur d'électricité et de gaz naturel. Démo produit — données et contenus fictifs.", es: "Proveedor de electricidad y gas natural. Demo de producto: datos y contenidos no reales." },
  "footer.colSite": { it: "Il sito", en: "The site", fr: "Le site", es: "El sitio" },
  "footer.colCustomerServices": { it: "Servizi Clienti", en: "Customer Services", fr: "Services Clients", es: "Servicios para Clientes" },
  "footer.colBecomeCustomer": { it: "Diventa Cliente", en: "Become a Customer", fr: "Devenir client", es: "Hazte cliente" },
  "footer.bottomCopy": { it: "© 2026 NovaLuce Energia S.p.A. — Sito demo, nessun dato reale.", en: "© 2026 NovaLuce Energia S.p.A. — Demo site, no real data.", fr: "© 2026 NovaLuce Energia S.p.A. — Site de démonstration, aucune donnée réelle.", es: "© 2026 NovaLuce Energia S.p.A. — Sitio de demostración, sin datos reales." },
  "footer.privacy": { it: "Privacy", en: "Privacy", fr: "Confidentialité", es: "Privacidad" },
  "footer.cookie": { it: "Cookie", en: "Cookies", fr: "Cookies", es: "Cookies" },
  "footer.terms": { it: "Termini", en: "Terms", fr: "Conditions", es: "Términos" },

  /* ---------- Login page ---------- */
  "login.title": { it: "Accedi all'Area Clienti", en: "Log in to the Customer Area", fr: "Connexion à l'Espace Client", es: "Acceder al Área de Clientes" },
  "login.subtitle": { it: "Gestisci la tua fornitura NovaLuce Energia: autolettura, bolletta web, voltura e molto altro.", en: "Manage your NovaLuce Energia supply: meter readings, paperless billing, holder change and more.", fr: "Gérez votre contrat NovaLuce Energia : relevé de compteur, facture dématérialisée, changement de titulaire et plus encore.", es: "Gestiona tu suministro NovaLuce Energia: autolectura, factura web, cambio de titular y mucho más." },
  "login.errorMsg": { it: "Credenziali non valide. Riprova oppure usa le credenziali demo qui sotto.", en: "Invalid credentials. Try again or use the demo credentials below.", fr: "Identifiants invalides. Réessayez ou utilisez les identifiants de démonstration ci-dessous.", es: "Credenciales no válidas. Inténtalo de nuevo o usa las credenciales de demostración de abajo." },
  "login.emailLabel": { it: "Email o codice cliente", en: "Email or customer code", fr: "Email ou code client", es: "Email o código de cliente" },
  "login.passwordLabel": { it: "Password", en: "Password", fr: "Mot de passe", es: "Contraseña" },
  "login.rememberMe": { it: "Ricordami", en: "Remember me", fr: "Se souvenir de moi", es: "Recuérdame" },
  "login.forgotPassword": { it: "Password dimenticata?", en: "Forgot your password?", fr: "Mot de passe oublié ?", es: "¿Olvidaste tu contraseña?" },
  "login.submit": { it: "Accedi", en: "Log In", fr: "Se connecter", es: "Acceder" },
  "login.demoHintPrefix": { it: "Demo: usa email", en: "Demo: use email", fr: "Démo : utilisez l'email", es: "Demo: usa el email" },
  "login.demoHintAnd": { it: "e password", en: "and password", fr: "et le mot de passe", es: "y la contraseña" },
  "login.demoHintSuffix": { it: "per accedere.", en: "to log in.", fr: "pour vous connecter.", es: "para acceder." },
  "login.noAccount": { it: "Non sei ancora cliente?", en: "Not a customer yet?", fr: "Pas encore client ?", es: "¿Todavía no eres cliente?" },
  "login.discoverLink": { it: "Scopri come attivare una fornitura", en: "Find out how to activate a supply", fr: "Découvrez comment activer un contrat", es: "Descubre cómo activar un suministro" },
  "login.redirectPrefix": { it: "Accedi per continuare verso:", en: "Log in to continue to:", fr: "Connectez-vous pour continuer vers :", es: "Accede para continuar hacia:" },

  /* ---------- Dashboard ---------- */
  "dashboard.eyebrow": { it: "Area Clienti", en: "Customer Area", fr: "Espace Client", es: "Área de Clientes" },
  "dashboard.title": { it: "I servizi della tua fornitura", en: "Your supply services", fr: "Les services de votre contrat", es: "Los servicios de tu suministro" },
  "dashboard.desc": { it: "Seleziona l'operazione che vuoi effettuare. Le richieste vengono gestite in autonomia, in pochi minuti.", en: "Select the operation you'd like to carry out. Requests are handled on your own, in just a few minutes.", fr: "Sélectionnez l'opération que vous souhaitez effectuer. Les demandes sont traitées en toute autonomie, en quelques minutes.", es: "Selecciona la operación que quieres realizar. Las solicitudes se gestionan de forma autónoma, en pocos minutos." },

  /* ---------- Prospect page ---------- */
  "pageHeader.eyebrow": { it: "Nuove forniture", en: "New supplies", fr: "Nouvelles fournitures", es: "Nuevos suministros" },
  "pageHeader.title": { it: "Diventa Cliente NovaLuce Energia", en: "Become a NovaLuce Energia Customer", fr: "Devenez client NovaLuce Energia", es: "Hazte cliente de NovaLuce Energia" },
  "pageHeader.desc": { it: "Scegli la procedura corretta per la tua situazione: ogni richiesta avvia un percorso guidato di firma digitale, senza bisogno di registrazione.", en: "Choose the right process for your situation: every request starts a guided digital signature journey, no registration needed.", fr: "Choisissez la démarche adaptée à votre situation : chaque demande lance un parcours de signature électronique guidé, sans inscription.", es: "Elige el trámite adecuado para tu situación: cada solicitud inicia un proceso guiado de firma digital, sin necesidad de registro." },
  "prospectSection.eyebrow": { it: "Procedure disponibili", en: "Available processes", fr: "Démarches disponibles", es: "Trámites disponibles" },
  "prospectSection.title": { it: "Seleziona il servizio che ti interessa", en: "Select the service you're interested in", fr: "Sélectionnez le service qui vous intéresse", es: "Selecciona el servicio que te interesa" },
  "prospectSection.desc": { it: "Ogni scheda avvia un percorso Docusign dedicato alla procedura scelta. Al termine della compilazione riceverai conferma via email.", en: "Each card starts a Docusign journey dedicated to the chosen process. You'll receive confirmation by email once it's completed.", fr: "Chaque fiche lance un parcours Docusign dédié à la démarche choisie. Vous recevrez une confirmation par email à la fin.", es: "Cada tarjeta inicia un proceso de Docusign dedicado al trámite elegido. Al finalizar recibirás confirmación por email." },
  "ctaLoginBanner.title": { it: "Sei già cliente NovaLuce Energia?", en: "Already a NovaLuce Energia customer?", fr: "Déjà client NovaLuce Energia ?", es: "¿Ya eres cliente de NovaLuce Energia?" },
  "ctaLoginBanner.desc": { it: "Accedi all'Area Clienti per gestire autolettura, bolletta web, voltura e altri servizi del tuo contratto.", en: "Log in to the Customer Area to manage meter readings, paperless billing, holder change and other services on your contract.", fr: "Connectez-vous à l'Espace Client pour gérer le relevé de compteur, la facture dématérialisée, le changement de titulaire et d'autres services de votre contrat.", es: "Accede al Área de Clientes para gestionar autolectura, factura web, cambio de titular y otros servicios de tu contrato." },

  /* ---------- Shared buttons ---------- */
  "common.request": { it: "Richiedi", en: "Request", fr: "Demander", es: "Solicitar" },
  "common.startProcedure": { it: "Avvia procedura", en: "Start process", fr: "Démarrer la procédure", es: "Iniciar trámite" },

  /* ---------- Toasts (JS-driven) ---------- */
  "toast.docusignNotConfigured": { it: "Link Docusign non ancora configurato per: {service}.", en: "Docusign link not yet configured for: {service}.", fr: "Lien Docusign pas encore configuré pour : {service}.", es: "Enlace de Docusign aún no configurado para: {service}." },
  "toast.serviceComingSoon": { it: "Funzionalità in arrivo: modulo per {service} collegato a Docusign via API.", en: "Coming soon: a form for {service} connected to Docusign via API.", fr: "Bientôt disponible : un formulaire pour {service} connecté à Docusign via API.", es: "Próximamente: un formulario para {service} conectado a Docusign vía API." },

  /* ---------- Category tags (service card pills) ---------- */
  "tag.contatore": { it: "Contatore", en: "Meter", fr: "Compteur", es: "Contador" },
  "tag.pagamenti": { it: "Pagamenti", en: "Payments", fr: "Paiements", es: "Pagos" },
  "tag.fatturazione": { it: "Fatturazione", en: "Billing", fr: "Facturation", es: "Facturación" },
  "tag.anagrafica": { it: "Anagrafica", en: "Contact Details", fr: "Coordonnées", es: "Datos personales" },
  "tag.documenti": { it: "Documenti", en: "Documents", fr: "Documents", es: "Documentos" },
  "tag.contratto": { it: "Contratto", en: "Contract", fr: "Contrat", es: "Contrato" },
  "tag.fornitura-attiva-altrove": { it: "Fornitura attiva altrove", en: "Active supply elsewhere", fr: "Contrat actif ailleurs", es: "Suministro activo en otra parte" },
  "tag.cambio-intestatario": { it: "Cambio intestatario", en: "Holder change", fr: "Changement de titulaire", es: "Cambio de titular" },
  "tag.nuovo-punto": { it: "Nuovo punto", en: "New connection point", fr: "Nouveau point", es: "Nuevo punto" },
  "tag.punto-mai-attivo": { it: "Punto mai attivo", en: "Never activated point", fr: "Point jamais activé", es: "Punto nunca activado" },
  "tag.aziende": { it: "Aziende", en: "Businesses", fr: "Entreprises", es: "Empresas" },
  "tag.nuovo-occupante": { it: "Nuovo occupante", en: "New occupant", fr: "Nouvel occupant", es: "Nuevo ocupante" },

  /* ---------- Service short glosses (subtitle under the fixed IT title) ---------- */
  "gloss.autolettura": { it: "Comunicazione lettura contatore", en: "Self-Meter Reading Submission", fr: "Transmission du relevé de compteur", es: "Envío de la autolectura del contador" },
  "gloss.domiciliazione-sepa": { it: "Addebito automatico in conto", en: "SEPA Direct Debit Setup/Change", fr: "Mise en place / modification du prélèvement SEPA", es: "Alta o cambio de domiciliación bancaria SEPA" },
  "gloss.bolletta-web": { it: "Fatturazione senza carta", en: "Paperless Billing Enrollment", fr: "Passage à la facture dématérialisée", es: "Alta en factura electrónica" },
  "gloss.variazione-recapito": { it: "Aggiornamento dei tuoi contatti", en: "Change of Contact Details", fr: "Modification des coordonnées", es: "Cambio de datos de contacto" },
  "gloss.estratto-conto": { it: "Riepilogo pagamenti e contratto", en: "Account Statement Request", fr: "Demande de relevé de compte", es: "Solicitud de extracto de cuenta" },
  "gloss.conferma-pagamento": { it: "Conferma pagamento su sollecito", en: "Payment Confirmation (reminder invoice)", fr: "Confirmation de paiement (facture de relance)", es: "Confirmación de pago (factura de aviso)" },
  "gloss.rimborso-bonifico": { it: "Richiesta rimborso su conto corrente", en: "Refund Request (bank transfer)", fr: "Demande de remboursement (virement bancaire)", es: "Solicitud de reembolso (transferencia bancaria)" },
  "gloss.voltura": { it: "Cambio intestatario del contratto", en: "Change of Contract Holder", fr: "Changement de titulaire du contrat", es: "Cambio de titular del contrato" },
  "gloss.disdetta-recesso": { it: "Chiusura del contratto in essere", en: "Contract Termination", fr: "Résiliation du contrat", es: "Baja / rescisión del contrato" },
  "gloss.switch": { it: "Cambio fornitore mantenendo il punto", en: "Supplier Change", fr: "Changement de fournisseur", es: "Cambio de compañía suministradora" },
  "gloss.voltura-contestuale": { it: "Cambio intestatario e fornitore insieme", en: "Simultaneous Holder Change + Switch", fr: "Changement de titulaire et de fournisseur simultané", es: "Cambio de titular y de compañía simultáneo" },
  "gloss.allaccio": { it: "Nuovo allacciamento alla rete", en: "New Connection", fr: "Nouveau raccordement au réseau", es: "Nueva conexión a la red" },
  "gloss.prima-attivazione": { it: "Prima attivazione su punto allacciato", en: "First Activation", fr: "Première mise en service", es: "Primera activación del suministro" },
  "gloss.business-piva": { it: "Fornitura dedicata alle aziende", en: "Business/VAT Contract Activation", fr: "Activation d'un contrat professionnel (TVA)", es: "Activación de contrato empresa (NIF/IVA)" },
  "gloss.subentro": { it: "Riattivazione per nuovo occupante", en: "Meter Reactivation for New Occupant", fr: "Réactivation du compteur pour un nouvel occupant", es: "Reactivación del contador para nuevo ocupante" },

  /* ---------- Service full descriptions ---------- */
  "desc.autolettura": { it: "Comunica la lettura del tuo contatore per ricevere bollette basate sui consumi reali.", en: "Submit your meter reading to receive bills based on your actual consumption.", fr: "Communiquez le relevé de votre compteur pour recevoir des factures basées sur votre consommation réelle.", es: "Comunica la lectura de tu contador para recibir facturas basadas en el consumo real." },
  "desc.domiciliazione-sepa": { it: "Attiva o modifica l'addebito automatico delle bollette sul tuo conto corrente.", en: "Set up or change automatic bill payment from your bank account.", fr: "Activez ou modifiez le prélèvement automatique de vos factures sur votre compte bancaire.", es: "Activa o modifica la domiciliación bancaria de tus facturas." },
  "desc.bolletta-web": { it: "Passa alla bolletta digitale: ricevi le fatture via email, senza carta.", en: "Switch to paperless billing: get your invoices by email, no paper.", fr: "Passez à la facture numérique : recevez vos factures par email, sans papier.", es: "Cambia a la factura digital: recibe tus facturas por email, sin papel." },
  "desc.variazione-recapito": { it: "Aggiorna indirizzo, email o numero di telefono associati al tuo contratto.", en: "Update the address, email or phone number linked to your contract.", fr: "Mettez à jour l'adresse, l'email ou le numéro de téléphone associés à votre contrat.", es: "Actualiza la dirección, el email o el número de teléfono de tu contrato." },
  "desc.estratto-conto": { it: "Richiedi il riepilogo dei pagamenti e della situazione contabile del tuo contratto.", en: "Request a summary of payments and the account status of your contract.", fr: "Demandez le récapitulatif des paiements et de la situation comptable de votre contrat.", es: "Solicita el resumen de pagos y la situación contable de tu contrato." },
  "desc.conferma-pagamento": { it: "Hai ricevuto un sollecito ma hai già pagato? Invia la conferma del pagamento.", en: "Received a reminder but already paid? Send us your payment confirmation.", fr: "Vous avez reçu une relance mais avez déjà payé ? Envoyez votre confirmation de paiement.", es: "¿Recibiste un aviso pero ya pagaste? Envía la confirmación del pago." },
  "desc.rimborso-bonifico": { it: "Richiedi il rimborso di un credito residuo tramite bonifico bancario.", en: "Request a refund of your outstanding credit via bank transfer.", fr: "Demandez le remboursement d'un crédit résiduel par virement bancaire.", es: "Solicita el reembolso de un saldo a favor mediante transferencia bancaria." },
  "desc.voltura": { it: "Trasferisci l'intestazione del contratto a un altro nominativo, mantenendo il POD/PDR.", en: "Transfer the contract to a new name, keeping the same POD/PDR.", fr: "Transférez le contrat à un autre titulaire, en conservant le même point de livraison (POD/PDR).", es: "Transfiere la titularidad del contrato a otra persona, manteniendo el mismo punto de suministro (POD/PDR)." },
  "desc.disdetta-recesso": { it: "Richiedi la chiusura o il recesso dal contratto di fornitura in essere.", en: "Request the closure or withdrawal from your current supply contract.", fr: "Demandez la clôture ou la résiliation de votre contrat de fourniture en cours.", es: "Solicita el cierre o la baja de tu contrato de suministro actual." },
  "desc.switch": { it: "Passa a NovaLuce Energia mantenendo lo stesso punto di fornitura, senza interruzioni del servizio.", en: "Switch to NovaLuce Energia keeping the same supply point, with no service interruption.", fr: "Passez à NovaLuce Energia en conservant le même point de fourniture, sans interruption de service.", es: "Cámbiate a NovaLuce Energia manteniendo el mismo punto de suministro, sin interrupciones." },
  "desc.voltura-contestuale": { it: "Cambia l'intestatario del contratto e passa a NovaLuce Energia in un'unica procedura.", en: "Change the contract holder and switch to NovaLuce Energia in a single process.", fr: "Changez le titulaire du contrat et passez à NovaLuce Energia en une seule procédure.", es: "Cambia el titular del contrato y pásate a NovaLuce Energia en un único trámite." },
  "desc.allaccio": { it: "Richiedi un nuovo allacciamento alla rete elettrica o del gas per un immobile mai servito prima.", en: "Request a new connection to the electricity or gas network for a property never supplied before.", fr: "Demandez un nouveau raccordement au réseau électrique ou gaz pour un logement jamais desservi.", es: "Solicita una nueva conexión a la red eléctrica o de gas para un inmueble sin suministro previo." },
  "desc.prima-attivazione": { it: "Attiva per la prima volta la fornitura di luce o gas su un punto già allacciato ma mai attivato.", en: "Activate electricity or gas for the first time on a point that's connected but never activated.", fr: "Activez pour la première fois la fourniture d'électricité ou de gaz sur un point déjà raccordé mais jamais activé.", es: "Activa por primera vez el suministro de luz o gas en un punto ya conectado pero nunca activado." },
  "desc.business-piva": { it: "Attiva una fornitura dedicata alla tua azienda o Partita IVA, con condizioni pensate per il business.", en: "Activate a supply dedicated to your business or VAT number, with terms designed for companies.", fr: "Activez une fourniture dédiée à votre entreprise ou numéro de TVA, avec des conditions pensées pour le business.", es: "Activa un suministro dedicado a tu empresa o NIF/IVA, con condiciones pensadas para negocios." },
  "desc.subentro": { it: "Riattiva il contatore a tuo nome subentrando in un immobile senza contratto attivo.", en: "Reactivate the meter in your name when moving into a property with no active contract.", fr: "Réactivez le compteur à votre nom en emménageant dans un logement sans contrat actif.", es: "Reactiva el contador a tu nombre al mudarte a un inmueble sin contrato activo." }
};
