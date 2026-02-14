const { NodeTypes } = require('/usr/local/lib/node_modules/n8n/dist/NodeTypes');
const nodeTypes = NodeTypes.getInstance();
nodeTypes.init().then(() => {
    const types = Object.keys(nodeTypes.nodeTypes);
    console.log(JSON.stringify(types, null, 2));
    process.exit(0);
}).catch(err => {
    console.error(err);
    process.exit(1);
});
