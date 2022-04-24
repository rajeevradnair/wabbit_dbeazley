# Project 9 - Generating WebAssembly

One possible target for your compiler is WebAssembly.  Go to the file `wabbit/wasm.py` and follow
the instructions at the top.

## Testing

If this part of the project is working, you should be able to take any
program in `tests/Programs/` and compile it to a WebAssembly file.
For example:

```
bash $ python3 -m wabbit.wasm tests/Programs/12_loop.wb
Wrote out.wasm
bash $ 
```

To test the program, you can run the `test.js` program using Node.  For example:

```
bash $ node test.js
... output from wabbit ...
bash $
```

Alternatively, you can run it in the browser.  Run a small web server in the top-level directory
like this:
```
bash $ python3 -m http.server
Serving HTTP on 0.0.0.0 port 8000 (http://0.0.0.0:8000/) ...
```

Now, click on
[http://localhost:8000/test.html](http://localhost:8000/test.html).
If it's working, you should see the program output in the browser.

## Hints

There are a lot of fiddly bits that can go wrong here. Debugging is
often difficult.  If you get no output at all, turn on the debugging
features of your browser. WebAssembly related errors are often
reported on the JavaScript console.

