/**
 * Three.js 3D animated logo: extruded look, Y rotation, float, soft glow, transparent background.
 * Optimized for web: single geometry, shared materials, requestAnimationFrame.
 */
(function (global) {
  'use strict';

  function initLogo3D(container, logoUrl) {
    if (!container || !global.THREE) return;

    var width = container.clientWidth || 360;
    var height = container.clientHeight || 360;
    var scene = new global.THREE.Scene();
    scene.background = null; // transparent

    var camera = new global.THREE.PerspectiveCamera(50, width / height, 0.1, 100);
    camera.position.set(0, 0, 1.9);
    camera.lookAt(0, 0, 0);

    var renderer = new global.THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setClearColor(0x000000, 0);
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(global.devicePixelRatio || 1, 2));
    renderer.outputColorSpace = global.THREE.SRGBColorSpace;
    renderer.toneMappingExposure = 0.88;
    container.appendChild(renderer.domElement);
    renderer.domElement.setAttribute('aria-hidden', 'true');

    var clock = new global.THREE.Clock();
    var mesh = null;
    var animationId = null;

    function buildMesh(texture) {
      texture.colorSpace = global.THREE.SRGBColorSpace;
      texture.needsUpdate = true;
      var image = texture.image;
      var w = image.naturalWidth || image.width || 1;
      var h = image.naturalHeight || image.height || 1;
      var aspect = h / w;
      var planeW = 1;
      var planeH = aspect;

      var logoMat = new global.THREE.MeshPhysicalMaterial({
        map: texture,
        transparent: true,
        alphaTest: 0.05,
        depthWrite: true,
        side: global.THREE.DoubleSide,
        emissive: 0x000000,
        emissiveIntensity: 0,
        metalness: 0.02,
        roughness: 0.55,
      });

      var geometry = new global.THREE.PlaneGeometry(planeW, planeH);
      mesh = new global.THREE.Mesh(geometry, logoMat);
      scene.add(mesh);
    }

    scene.add(new global.THREE.AmbientLight(0xffffff, 0.75));
    var keyLight = new global.THREE.DirectionalLight(0xffffff, 0.85);
    keyLight.position.set(0, 0.25, 2);
    scene.add(keyLight);
    var fillLight = new global.THREE.DirectionalLight(0xffffff, 0.45);
    fillLight.position.set(-0.8, 0, 1.5);
    scene.add(fillLight);
    var backLight = new global.THREE.DirectionalLight(0xffffff, 0.22);
    backLight.position.set(0, 0, -1);
    scene.add(backLight);

    var loader = new global.THREE.TextureLoader();
    loader.load(
      logoUrl,
      function (texture) {
        buildMesh(texture);
        var fallback = container.querySelector('.logo-3d-fallback');
        if (fallback) fallback.style.display = 'none';
      },
      undefined,
      function () {
        var fallback = container.querySelector('.logo-3d-fallback');
        if (fallback) fallback.style.display = 'block';
      }
    );

    function animate() {
      animationId = requestAnimationFrame(animate);
      var t = clock.getElapsedTime();
      if (mesh) {
        mesh.rotation.y = Math.sin(t * 0.25) * 0.22;
        mesh.position.y = Math.sin(t * 0.3) * 0.03;
      }
      renderer.render(scene, camera);
    }
    animate();

    function onResize() {
      var w = container.clientWidth || width;
      var h = container.clientHeight || height;
      if (w === 0 || h === 0) return;
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
      renderer.setSize(w, h);
    }
    global.addEventListener('resize', onResize);

    return {
      destroy: function () {
        cancelAnimationFrame(animationId);
        global.removeEventListener('resize', onResize);
        if (renderer.domElement && renderer.domElement.parentNode)
          renderer.domElement.parentNode.removeChild(renderer.domElement);
        renderer.dispose();
        if (mesh && mesh.geometry) mesh.geometry.dispose();
        if (mesh && mesh.material) {
          var mats = Array.isArray(mesh.material) ? mesh.material : [mesh.material];
          mats.forEach(function (m) { if (m.map) m.map.dispose(); m.dispose(); });
        }
      }
    };
  }

  global.initLogo3D = initLogo3D;
})(typeof window !== 'undefined' ? window : this);
