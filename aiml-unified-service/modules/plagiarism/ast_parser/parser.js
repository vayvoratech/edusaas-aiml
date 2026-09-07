const acorn = require("acorn");

let source = "";


// ============================================================
// READ SOURCE CODE
// ============================================================

process.stdin.on("data", (chunk) => {
    source += chunk;
});


process.stdin.on("end", () => {

    try {

        let ast;


        // ====================================================
        // FIRST: TRY ES MODULE
        // ====================================================

        try {

            ast = acorn.parse(
                source,
                {
                    ecmaVersion: "latest",
                    sourceType: "module",
                    locations: true,
                    ranges: true,
                    allowHashBang: true
                }
            );

        } catch (moduleError) {

            // ================================================
            // FALLBACK: SCRIPT / COMMONJS
            // ================================================

            ast = acorn.parse(
                source,
                {
                    ecmaVersion: "latest",
                    sourceType: "script",
                    locations: true,
                    ranges: true,
                    allowHashBang: true
                }
            );
        }


        // ====================================================
        // RETURN AST
        // ====================================================

        process.stdout.write(
            JSON.stringify(ast)
        );


    } catch (error) {

        // ====================================================
        // PARSING ERROR
        // ====================================================

        process.stderr.write(
            JSON.stringify({
                error: error.message
            })
        );

        process.exit(1);
    }
});